"""Section 3 / 7: Factory pattern for creating products."""
import ast
import inspect
import unittest
from pathlib import Path

import inventory_manager
from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

PROJECT_DIR = Path(__file__).resolve().parent.parent


class TestProductFactory(unittest.TestCase):

    def setUp(self):
        self.supplier = Supplier("S1", "TechWorld", "sales@techworld.example")

    def test_creates_physical_product(self):
        product = ProductFactory.create("physical", "P1", "Desk Lamp", 25.0, 10,
                                        self.supplier, weight=1.5)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertEqual(product.get_weight(), 1.5)
        self.assertIs(product.get_supplier(), self.supplier)

    def test_creates_digital_product(self):
        product = ProductFactory.create("digital", "D1", "Photo Editor", 49.9, 100,
                                        self.supplier, download_size=850.0)
        self.assertIsInstance(product, DigitalProduct)
        self.assertEqual(product.get_download_size(), 850.0)

    def test_extra_details_default_to_zero(self):
        # The products CSV has no weight / download size columns.
        lamp = ProductFactory.create("physical", "P1", "Desk Lamp", 25.0, 10, self.supplier)
        self.assertEqual(lamp.get_weight(), 0.0)

    def test_unknown_type_raises_clear_value_error(self):
        with self.assertRaises(ValueError) as context:
            ProductFactory.create("service", "S1", "Installation", 30.0, 5, self.supplier)
        self.assertEqual(str(context.exception), "Unknown product type: service")

    def test_create_is_static_and_returns_product(self):
        self.assertIsInstance(inspect.getattr_static(ProductFactory, "create"), staticmethod)
        hints = inspect.get_annotations(ProductFactory.create, eval_str=True)
        self.assertIs(hints["return"], Product)

    def test_factory_applies_product_validation(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P1", "Lamp", 0.0, 10, self.supplier)


class TestProductsCreatedThroughFactory(unittest.TestCase):
    """The main program never creates PhysicalProduct / DigitalProduct directly."""

    def setUp(self):
        source = (PROJECT_DIR / "inventory_manager.py").read_text(encoding="utf-8")
        self.tree = ast.parse(source)

    def test_no_direct_constructor_calls(self):
        direct = [node.func.id for node in ast.walk(self.tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id in ("PhysicalProduct", "DigitalProduct")]
        self.assertEqual(direct, [])

    def test_concrete_classes_not_imported(self):
        imported = {alias.name for node in ast.walk(self.tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                    for alias in node.names}
        self.assertNotIn("PhysicalProduct", imported)
        self.assertNotIn("DigitalProduct", imported)
        self.assertIn("ProductFactory", imported)

    def test_default_inventory_still_has_both_types(self):
        inventory = inventory_manager.default_inventory(inventory_manager.default_suppliers())
        self.assertIsInstance(inventory.find_product("P001"), PhysicalProduct)
        self.assertIsInstance(inventory.find_product("D001"), DigitalProduct)

    def test_saved_data_rebuilt_through_factory(self):
        suppliers = inventory_manager.default_suppliers()
        item = {"id": "D9", "name": "Antivirus", "price": 49.99, "stock": 200,
                "supplier_id": "S003", "type": "digital", "download_size": 300.0}
        product = inventory_manager.product_from_dict(item, suppliers)
        self.assertIsInstance(product, DigitalProduct)
        self.assertIs(product.get_supplier(), suppliers["S003"])

    def test_saved_data_with_unknown_type_rejected(self):
        suppliers = inventory_manager.default_suppliers()
        item = {"id": "X1", "name": "Mystery", "price": 1.0, "stock": 1,
                "supplier_id": "S001", "type": "bundle"}
        with self.assertRaises(ValueError):
            inventory_manager.product_from_dict(item, suppliers)


if __name__ == "__main__":
    unittest.main(verbosity=2)
