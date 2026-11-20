"""Section 5 / 7: exceptions are handled gracefully and specifically."""
import ast
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import inventory_manager
from inventory import Inventory
from supplier import Supplier

PROJECT_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_CSV = PROJECT_DIR / "products.csv"


def run_quietly(func, *args):
    """Run func and return (result, everything it printed)."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = func(*args)
    return result, buffer.getvalue()


class TestUserInput(unittest.TestCase):

    def test_get_positive_float_keeps_asking(self):
        # Predict first 5.1: abc, then -5, then 12.50
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]):
            value, output = run_quietly(inventory_manager.get_positive_float, "Price: ")
        self.assertEqual(value, 12.5)
        self.assertEqual(output.splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_get_positive_float_rejects_zero(self):
        with patch("builtins.input", side_effect=["0", "3"]):
            value, output = run_quietly(inventory_manager.get_positive_float, "Price: ")
        self.assertEqual(value, 3.0)
        self.assertIn("greater than zero", output)

    def test_get_whole_number_keeps_asking(self):
        with patch("builtins.input", side_effect=["two", "2.5", "-1", "0"]):
            value, output = run_quietly(inventory_manager.get_whole_number, "Stock: ", 0)
        self.assertEqual(value, 0)
        self.assertEqual(output.splitlines(), [
            "Please enter a valid whole number, e.g. 5",
            "Please enter a valid whole number, e.g. 5",
            "Please enter a whole number of 0 or more.",
        ])

    def test_order_quantity_must_be_at_least_one(self):
        with patch("builtins.input", side_effect=["0", "4"]):
            value, output = run_quietly(inventory_manager.get_whole_number, "Qty: ", 1)
        self.assertEqual(value, 4)
        self.assertIn("1 or more", output)

    def test_invalid_menu_input_does_not_crash_add_product(self):
        inventory = Inventory()
        suppliers = inventory_manager.default_suppliers()
        answers = ["1", "P9", "Desk", "abc", "-2", "45", "-1", "3", "0", "2.5", "S001"]
        with patch("builtins.input", side_effect=answers):
            _, output = run_quietly(inventory_manager.add_product_menu, inventory, suppliers)
        product = inventory.find_product("P9")
        self.assertEqual(product.get_price(), 45.0)
        self.assertEqual(product.get_stock(), 3)
        self.assertEqual(product.get_weight(), 2.5)
        self.assertIn("Product added successfully!", output)


class TestLoadProducts(unittest.TestCase):

    def setUp(self):
        self.inventory = Inventory("CSV test")
        self.supplier = Supplier("S9", "Office Supplies Co", "orders@office.example")

    def test_bad_rows_skipped_and_valid_rows_load(self):
        # Predict first 5.2: 3 products, messages in this exact order.
        _, output = run_quietly(inventory_manager.load_products,
                                str(PRODUCTS_CSV), self.inventory, self.supplier)
        self.assertEqual(output.splitlines(), [
            "Line 4 skipped: Unknown product type: service",
            "Line 5 skipped: could not convert string to float: 'abc'",
            "3 products loaded.",
            "Load attempt finished.",
        ])
        ids = [product.get_product_id() for product in self.inventory.products]
        self.assertEqual(ids, ["P001", "D001", "P003"])
        self.assertIs(self.inventory.find_product("P003").get_supplier(), self.supplier)

    def test_missing_file_handled_gracefully(self):
        # Predict first 5.2 (renamed file): except + finally run, else does not.
        with tempfile.TemporaryDirectory() as folder:
            shutil.copy(PRODUCTS_CSV, os.path.join(folder, "products_renamed.csv"))
            path = os.path.join(folder, "products.csv")
            _, output = run_quietly(inventory_manager.load_products,
                                    path, self.inventory, self.supplier)
        self.assertEqual(output.splitlines(), [
            f"Products file not found: {path}",
            "Load attempt finished.",
        ])
        self.assertEqual(self.inventory.products, [])

    def test_duplicates_wrong_columns_and_invalid_values_skipped(self):
        rows = ("product_type,product_id,name,price,stock_quantity\n"
                "physical,P1,Lamp,25.00,10\n"
                "physical,P1,Lamp again,25.00,10\n"
                "digital,D1,Too few columns\n"
                "\n"
                "digital,D2,Free App,0,10\n"
                "physical,P2,Chair,80.00,-4\n"
                "digital,D3,Editor,49.90,100\n")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "products.csv")
            with open(path, "w", encoding="utf-8", newline="") as file:
                file.write(rows)
            _, output = run_quietly(inventory_manager.load_products,
                                    path, self.inventory, self.supplier)
        self.assertIn("Line 3 skipped: product ID P1 already exists.", output)
        self.assertIn("Line 4 skipped: not enough values to unpack", output)
        self.assertIn("Line 6 skipped: Price must be greater than zero.", output)
        self.assertIn("Line 7 skipped: Stock quantity", output)
        self.assertIn("2 products loaded.", output)
        self.assertTrue(output.endswith("Load attempt finished.\n"))


class TestInventoryFileErrors(unittest.TestCase):

    def run_load_data_with(self, content: str | None):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "inventory.json")
            if content is not None:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
            with patch.object(inventory_manager, "INVENTORY_FILE", path):
                return run_quietly(inventory_manager.load_data)

    def test_missing_inventory_file_uses_defaults(self):
        (inventory, _), output = self.run_load_data_with(None)
        self.assertIn("No existing inventory file found", output)
        self.assertIsNotNone(inventory.find_product("P001"))

    def test_corrupt_json_falls_back_to_defaults(self):
        (inventory, _), output = self.run_load_data_with("{ this is not json")
        self.assertIn("Error loading", output)
        self.assertIsNotNone(inventory.find_product("P001"))

    def test_invalid_saved_price_falls_back_to_defaults(self):
        data = {"suppliers": [{"id": "S1", "name": "A", "email": "a@a"}],
                "products": [{"id": "P1", "name": "Bad", "price": -3, "stock": 1,
                              "supplier_id": "S1", "type": "physical", "weight": 1.0}]}
        (inventory, _), output = self.run_load_data_with(json.dumps(data))
        self.assertIn("Price must be greater than zero.", output)
        self.assertIsNone(inventory.find_product("P1"))

    def test_missing_field_falls_back_to_defaults(self):
        (_, suppliers), output = self.run_load_data_with(json.dumps({"products": []}))
        self.assertIn("Error loading", output)
        self.assertIn("S001", suppliers)


class TestExceptsAreSpecific(unittest.TestCase):
    """No bare `except:` and no catch-all `except Exception` in the project."""

    def test_every_except_names_a_specific_exception(self):
        too_broad = {"Exception", "BaseException"}
        problems = []
        for path in PROJECT_DIR.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                if node.type is None:
                    problems.append(f"{path.name}:{node.lineno} bare except")
                    continue
                names = node.type.elts if isinstance(node.type, ast.Tuple) else [node.type]
                for name in names:
                    if isinstance(name, ast.Name) and name.id in too_broad:
                        problems.append(f"{path.name}:{node.lineno} except {name.id}")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
