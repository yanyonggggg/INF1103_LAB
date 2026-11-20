"""Lab 8 checks kept as regression tests, so the Lab 9 changes did not break
association, aggregation, composition, LSP, polymorphism or persistence.

Changed from Lab 8: update_stock() now raises ValueError for an invalid
quantity instead of returning False (Lab 9 validation).
"""
import gc
import inspect
import io
import json
import os
import tempfile
import unittest
import weakref
from contextlib import redirect_stdout

import inventory_manager
from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


def captured(func, *args) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        func(*args)
    return buffer.getvalue()


class TestAssociation(unittest.TestCase):
    """Supplier and Product know about each other but neither owns the other."""

    def setUp(self):
        self.supplier = Supplier("S1", "Melody Music Supply", "orders@melody.example")
        self.guitar = PhysicalProduct("P1", "Guitar", 450.0, 5, self.supplier, 3.5)
        self.app = DigitalProduct("D1", "Music App", 89.0, 30, self.supplier, 1200.0)

    def test_product_stores_reference_to_supplier(self):
        self.assertIs(self.guitar.get_supplier(), self.supplier)
        self.assertIs(self.app.get_supplier(), self.supplier)

    def test_supplier_information_through_product(self):
        output = captured(self.guitar.display_supplier_information)
        self.assertIn("Melody Music Supply", output)
        self.assertIn("orders@melody.example", output)

    def test_products_keep_supplier_after_del(self):
        supplier = Supplier("S3", "Temp Co", "t@temp.example")
        product = PhysicalProduct("P2", "Drum", 99.0, 1, supplier, 4.0)
        del supplier
        self.assertEqual(product.get_supplier().get_name(), "Temp Co")

    def test_product_and_supplier_have_separate_lifecycles(self):
        product_ref = weakref.ref(self.guitar)
        self.guitar = None
        gc.collect()
        self.assertIsNone(product_ref())
        self.assertEqual(self.supplier.get_name(), "Melody Music Supply")


class TestAggregation(unittest.TestCase):
    """Inventory groups Products but does not control their lifecycle."""

    def setUp(self):
        supplier = Supplier("S1", "TechWorld", "sales@techworld.example")
        self.laptop = PhysicalProduct("P1", "Laptop", 1200.0, 15, supplier, 2.0)
        self.inventory_a = Inventory("A")
        self.inventory_b = Inventory("B")

    def test_add_find_and_duplicate(self):
        self.assertTrue(self.inventory_a.add_product(self.laptop))
        self.assertFalse(self.inventory_a.add_product(self.laptop))
        self.assertIs(self.inventory_a.find_product("p1"), self.laptop)
        self.assertIsNone(self.inventory_a.find_product("NOPE"))

    def test_remove_does_not_destroy_product(self):
        self.inventory_a.add_product(self.laptop)
        removed = self.inventory_a.remove_product("P1")
        self.assertIs(removed, self.laptop)
        self.assertIsNone(self.inventory_a.find_product("P1"))
        self.laptop.update_stock(3)
        self.assertEqual(self.laptop.get_stock(), 3)

    def test_transfer_product(self):
        self.inventory_a.add_product(self.laptop)
        self.assertTrue(self.inventory_a.transfer_product("P1", self.inventory_b))
        self.assertIsNone(self.inventory_a.find_product("P1"))
        self.assertIs(self.inventory_b.find_product("P1"), self.laptop)
        self.assertFalse(self.inventory_a.transfer_product("P1", self.inventory_b))

    def test_clearing_inventory_keeps_products(self):
        self.inventory_a.add_product(self.laptop)
        self.inventory_a.clear()
        self.assertEqual(self.inventory_a.products, [])
        self.assertEqual(self.laptop.get_name(), "Laptop")

    def test_products_property_is_a_copy(self):
        self.inventory_a.add_product(self.laptop)
        self.inventory_a.products.clear()
        self.assertIs(self.inventory_a.find_product("P1"), self.laptop)


class TestComposition(unittest.TestCase):
    """Order creates and manages its own OrderLine objects."""

    def setUp(self):
        supplier = Supplier("S1", "TechWorld", "sales@techworld.example")
        self.laptop = PhysicalProduct("P1", "Laptop", 1200.0, 15, supplier, 2.0)
        self.mouse = PhysicalProduct("P2", "Mouse", 25.5, 40, supplier, 0.1)
        self.os_product = DigitalProduct("D1", "OS", 139.99, 100, supplier, 5200.0)

    def test_order_creates_its_own_order_lines(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 1)
        order.add_order_line(self.mouse, 2)
        lines = order.get_order_lines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(isinstance(line, OrderLine) for line in lines))
        params = list(inspect.signature(Order.add_order_line).parameters)
        self.assertEqual(params, ["self", "product", "quantity"])

    def test_order_lines_cannot_be_changed_from_outside(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 1)
        self.assertIsInstance(order.get_order_lines(), tuple)

    def test_subtotal_and_total_without_discount(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 1)      # 1200.00
        order.add_order_line(self.mouse, 2)       #   51.00
        order.add_order_line(self.os_product, 1)  #  139.99
        self.assertAlmostEqual(order.get_order_lines()[1].calculate_subtotal(), 51.0)
        self.assertAlmostEqual(order.calculate_total(), 1390.99)

    def test_same_product_in_two_orders_gives_two_lines_one_product(self):
        order_1 = Order("O1")
        order_2 = Order("O2")
        order_1.add_order_line(self.laptop, 1)
        order_2.add_order_line(self.laptop, 3)
        line_1 = order_1.get_order_lines()[0]
        line_2 = order_2.get_order_lines()[0]
        self.assertIsNot(line_1, line_2)
        self.assertIs(line_1.get_product(), line_2.get_product())

    def test_remove_order_line_leaves_product(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 2)
        self.assertTrue(order.remove_order_line("P1"))
        self.assertEqual(order.get_order_lines(), ())
        self.assertEqual(self.laptop.get_name(), "Laptop")

    def test_order_lines_die_with_order(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 1)
        line_ref = weakref.ref(order.get_order_lines()[0])
        del order
        gc.collect()
        self.assertIsNone(line_ref())
        self.assertEqual(self.laptop.get_name(), "Laptop")


class TestLSPAndPolymorphism(unittest.TestCase):

    def setUp(self):
        supplier = Supplier("S1", "TechWorld", "sales@techworld.example")
        self.guitar = PhysicalProduct("P1", "Guitar", 450.0, 5, supplier, 3.5)
        self.editor = DigitalProduct("D1", "Photo Editor", 59.0, 50, supplier, 850.0)
        self.products: list[Product] = [self.guitar, self.editor]

    def test_product_is_abstract(self):
        with self.assertRaises(TypeError):
            Product("X1", "Generic", 1.0, 1, Supplier("S", "S", "s@s"))

    def test_update_stock_contract_preserved_by_both(self):
        for product in self.products:
            with self.subTest(product=product.get_name()):
                product.update_stock(0)
                product.update_stock(25)
                self.assertEqual(product.get_stock(), 25)
                with self.assertRaises(ValueError):
                    product.update_stock(-1)
                with self.assertRaises(ValueError):
                    product.update_stock("ten")
                self.assertEqual(product.get_stock(), 25)

    def test_polymorphic_calls_pick_subclass_implementation(self):
        inventory = Inventory()
        for product in self.products:
            inventory.add_product(product)
        info = [product.get_fulfilment_info() for product in inventory.products]
        self.assertIn("physical shipping", info[0])
        self.assertIn("delivered digitally", info[1])
        output = captured(inventory.display_all_products)
        self.assertIn("Weight: 3.50 kg", output)
        self.assertIn("Download size: 850.00 MB", output)

    def test_shipping_interface_only_on_physical(self):
        self.assertIsInstance(self.guitar, CanBeShipped)
        self.assertNotIsInstance(self.editor, CanBeShipped)


class TestPersistence(unittest.TestCase):

    def test_save_and_load_keeps_types_and_suppliers(self):
        suppliers = inventory_manager.default_suppliers()
        inventory = inventory_manager.default_inventory(suppliers)

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "inventory.json")
            original = inventory_manager.INVENTORY_FILE
            inventory_manager.INVENTORY_FILE = path
            try:
                with redirect_stdout(io.StringIO()):
                    inventory_manager.save_data(inventory, suppliers)
                    loaded, loaded_suppliers = inventory_manager.load_data()
                with open(path, encoding="utf-8") as file:
                    saved = json.load(file)
            finally:
                inventory_manager.INVENTORY_FILE = original

        self.assertEqual(len(saved["suppliers"]), 3)
        self.assertEqual(saved["products"][0]["supplier_id"], "S001")
        laptop = loaded.find_product("P001")
        self.assertIsInstance(laptop, PhysicalProduct)
        self.assertIsInstance(loaded.find_product("D001"), DigitalProduct)
        self.assertIs(laptop.get_supplier(), loaded_suppliers["S001"])
        self.assertIs(loaded.find_product("P002").get_supplier(), laptop.get_supplier())


if __name__ == "__main__":
    unittest.main(verbosity=2)
