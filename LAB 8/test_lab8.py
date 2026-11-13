"""Lab 8 checks (section 9). Run with: python test_lab8.py"""
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
from supplier import Supplier
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from can_be_shipped import CanBeShipped
from inventory import Inventory
from order import Order
from order_line import OrderLine


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

    def test_supplier_exists_without_products(self):
        alone = Supplier("S2", "Lonely Ltd", "hi@lonely.example")
        self.assertIn("Lonely Ltd", captured(alone.display_information))

    def test_products_keep_supplier_after_del(self):
        supplier = Supplier("S3", "Temp Co", "t@temp.example")
        product = PhysicalProduct("P2", "Drum", 99.0, 1, supplier, 4.0)
        del supplier
        self.assertEqual(product.get_supplier().get_name(), "Temp Co")

    def test_product_survives_when_supplier_reference_is_gone(self):
        # Removing everything else that points at the product leaves the
        # Supplier untouched, and vice versa: separate lifecycles.
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
        self.os_product = DigitalProduct("D1", "OS", 139.99, 100, supplier, 5200.0)
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
        self.assertTrue(self.laptop.update_stock(3))
        self.assertIn("Laptop", captured(self.laptop.display_information))

    def test_remove_missing_returns_none(self):
        self.assertIsNone(self.inventory_a.remove_product("NOPE"))

    def test_same_product_moves_to_another_inventory(self):
        self.inventory_a.add_product(self.laptop)
        self.inventory_a.remove_product("P1")
        self.inventory_b.add_product(self.laptop)
        self.assertIs(self.inventory_b.find_product("P1"), self.laptop)

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
        # add_order_line takes a Product and a quantity, not an OrderLine.
        params = list(inspect.signature(Order.add_order_line).parameters)
        self.assertEqual(params, ["self", "product", "quantity"])

    def test_order_lines_cannot_be_changed_from_outside(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 1)
        self.assertIsInstance(order.get_order_lines(), tuple)

    def test_order_line_refers_to_but_does_not_own_product(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 2)
        line = order.get_order_lines()[0]
        self.assertIs(line.get_product(), self.laptop)
        order.remove_order_line("P1")
        self.assertEqual(order.get_order_lines(), ())
        self.assertEqual(self.laptop.get_name(), "Laptop")  # product unaffected

    def test_subtotal_and_total(self):
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

    def test_order_lines_die_with_order(self):
        order = Order("O1")
        order.add_order_line(self.laptop, 1)
        line_ref = weakref.ref(order.get_order_lines()[0])
        del order
        gc.collect()
        self.assertIsNone(line_ref())                   # part is gone
        self.assertEqual(self.laptop.get_name(), "Laptop")  # product is not

    def test_invalid_quantity_rejected(self):
        order = Order("O1")
        with self.assertRaises(ValueError):
            order.add_order_line(self.laptop, 0)
        self.assertAlmostEqual(order.calculate_total(), 0.0)


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
                self.assertTrue(product.update_stock(0))
                self.assertTrue(product.update_stock(25))
                self.assertEqual(product.get_stock(), 25)
                self.assertFalse(product.update_stock(-1))
                self.assertFalse(product.update_stock("ten"))
                self.assertEqual(product.get_stock(), 25)

    def test_fulfilment_info_returns_str_for_both(self):
        for product in self.products:
            with self.subTest(product=product.get_name()):
                self.assertIsInstance(product.get_fulfilment_info(), str)

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

    def test_show_product_details_works_for_both(self):
        from lab8_demo import show_product_details
        self.assertIn("physical shipping", captured(show_product_details, self.guitar))
        self.assertIn("delivered digitally", captured(show_product_details, self.editor))

    def test_shipping_interface_only_on_physical(self):
        self.assertIsInstance(self.guitar, CanBeShipped)
        self.assertNotIsInstance(self.editor, CanBeShipped)


class TestTypeHints(unittest.TestCase):
    """Type hints match the UML design."""

    def hints(self, func):
        return inspect.get_annotations(func, eval_str=True)

    def test_constructor_and_method_hints(self):
        self.assertIs(self.hints(Product.__init__)["supplier"], Supplier)
        self.assertEqual(self.hints(Inventory.find_product)["return"], Product | None)
        self.assertEqual(self.hints(Inventory.remove_product)["product_id"], str)
        self.assertIs(self.hints(Inventory.add_product)["product"], Product)
        self.assertIs(self.hints(Order.add_order_line)["product"], Product)
        self.assertIs(self.hints(Order.add_order_line)["quantity"], int)
        self.assertIsNone(self.hints(Order.add_order_line)["return"])
        self.assertIs(self.hints(Order.calculate_total)["return"], float)
        self.assertIs(self.hints(OrderLine.calculate_subtotal)["return"], float)
        self.assertIs(self.hints(OrderLine.__init__)["product"], Product)
        self.assertEqual(self.hints(Inventory.transfer_product)["target"], Inventory)

    def test_collection_hints_in_source(self):
        self.assertIn("list[Product]", inspect.getsource(Inventory.__init__))
        self.assertIn("list[OrderLine]", inspect.getsource(Order.__init__))
        self.assertIn("self.__supplier: Supplier", inspect.getsource(Product.__init__))


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
                with open(path) as file:
                    saved = json.load(file)
            finally:
                inventory_manager.INVENTORY_FILE = original

        self.assertEqual(len(saved["suppliers"]), 3)
        self.assertEqual(saved["products"][0]["supplier_id"], "S001")
        laptop = loaded.find_product("P001")
        os_product = loaded.find_product("D001")
        self.assertIsInstance(laptop, PhysicalProduct)
        self.assertIsInstance(os_product, DigitalProduct)
        # Products loaded with the same supplier share one Supplier object.
        self.assertIs(laptop.get_supplier(), loaded_suppliers["S001"])
        self.assertIs(loaded.find_product("P002").get_supplier(), laptop.get_supplier())


if __name__ == "__main__":
    unittest.main(verbosity=2)
