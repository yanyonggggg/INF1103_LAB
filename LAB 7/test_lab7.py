"""Lab 7 checks (section 7). Run with: python test_lab7.py"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import inventory_manager
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from can_be_shipped import CanBeShipped
from inventory import Inventory


def captured_display(product):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        product.display_information()
    return buffer.getvalue()


class TestLab7(unittest.TestCase):

    def setUp(self):
        self.guitar = PhysicalProduct("P100", "Guitar", 450.0, 5, 3.5)
        self.os_product = DigitalProduct("D100", "Operating System", 139.99, 100, 5200.0)

    def test_physical_stores_and_displays_weight(self):
        self.assertEqual(self.guitar.get_weight(), 3.5)
        output = captured_display(self.guitar)
        self.assertIn("Name: Guitar", output)      # from parent
        self.assertIn("Weight: 3.50 kg", output)   # from child

    def test_digital_stores_and_displays_download_size(self):
        self.assertEqual(self.os_product.get_download_size(), 5200.0)
        output = captured_display(self.os_product)
        self.assertIn("Name: Operating System", output)
        self.assertIn("Download size: 5200.00 MB", output)

    def test_both_implement_fulfilment_info(self):
        self.assertIn("physical shipping", self.guitar.get_fulfilment_info())
        self.assertIn("delivered digitally", self.os_product.get_fulfilment_info())

    def test_product_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Product("X1", "Generic", 1.0, 1)

    def test_shipping_cost_depends_on_weight(self):
        light = PhysicalProduct("P1", "Mouse", 25.5, 1, 0.1)
        heavy = PhysicalProduct("P2", "Amplifier", 300.0, 1, 20.0)
        self.assertAlmostEqual(light.calculate_shipping_cost(), 5.25)
        self.assertAlmostEqual(heavy.calculate_shipping_cost(), 55.0)
        self.assertIsInstance(light, CanBeShipped)

    def test_digital_is_not_shippable(self):
        self.assertNotIsInstance(self.os_product, CanBeShipped)
        self.assertFalse(hasattr(self.os_product, "calculate_shipping_cost"))

    def test_inventory_operations(self):
        inventory = Inventory()
        self.assertTrue(inventory.add_product(self.guitar))
        self.assertTrue(inventory.add_product(self.os_product))
        self.assertFalse(inventory.add_product(self.guitar))  # duplicate ID
        self.assertIs(inventory.search_product("p100"), self.guitar)
        self.assertIsNone(inventory.search_product("NOPE"))
        self.assertTrue(self.guitar.update_stock(9))
        self.assertEqual(self.guitar.get_stock(), 9)
        self.assertFalse(self.guitar.update_stock(-1))

    def test_json_save_and_load_keeps_types(self):
        inventory = Inventory()
        inventory.add_product(self.guitar)
        inventory.add_product(self.os_product)

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "inventory.json")
            original = inventory_manager.INVENTORY_FILE
            inventory_manager.INVENTORY_FILE = path
            try:
                with redirect_stdout(io.StringIO()):
                    inventory_manager.save_inventory(inventory)
                    loaded = inventory_manager.load_inventory()
                with open(path) as file:
                    saved = json.load(file)
            finally:
                inventory_manager.INVENTORY_FILE = original

        self.assertEqual([item["type"] for item in saved], ["physical", "digital"])
        guitar = loaded.search_product("P100")
        os_product = loaded.search_product("D100")
        self.assertIsInstance(guitar, PhysicalProduct)
        self.assertIsInstance(os_product, DigitalProduct)
        self.assertEqual(guitar.get_weight(), 3.5)
        self.assertEqual(os_product.get_download_size(), 5200.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
