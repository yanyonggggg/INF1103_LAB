"""Section 4 / 7: validation rules live in the class that owns them."""
import unittest

from digital_product import DigitalProduct
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from supplier import Supplier


class TestProductValidation(unittest.TestCase):

    def setUp(self):
        self.supplier = Supplier("S1", "TechWorld", "sales@techworld.example")

    def test_price_must_be_greater_than_zero(self):
        for bad_price in (0, 0.0, -5.0):
            with self.subTest(price=bad_price):
                with self.assertRaises(ValueError) as context:
                    PhysicalProduct("P1", "Lamp", bad_price, 10, self.supplier, 1.0)
                self.assertEqual(str(context.exception), "Price must be greater than zero.")

    def test_price_must_be_a_number(self):
        with self.assertRaises(ValueError):
            PhysicalProduct("P1", "Lamp", "25", 10, self.supplier, 1.0)

    def test_stock_cannot_be_negative_when_created(self):
        with self.assertRaises(ValueError) as context:
            PhysicalProduct("P1", "Lamp", 25.0, -1, self.supplier, 1.0)
        self.assertIn("cannot be negative", str(context.exception))

    def test_zero_stock_and_small_price_are_valid(self):
        product = PhysicalProduct("P1", "Lamp", 0.01, 0, self.supplier, 1.0)
        self.assertEqual(product.get_stock(), 0)

    def test_update_stock_rejects_invalid_and_keeps_old_value(self):
        product = PhysicalProduct("P1", "Lamp", 25.0, 10, self.supplier, 1.0)
        for bad in (-1, "ten", 2.5):
            with self.subTest(quantity=bad):
                with self.assertRaises(ValueError):
                    product.update_stock(bad)
                self.assertEqual(product.get_stock(), 10)
        product.update_stock(0)
        self.assertEqual(product.get_stock(), 0)

    def test_digital_product_keeps_the_same_rules(self):
        # LSP: the subclass may not skip or change Product's rules.
        with self.assertRaises(ValueError):
            DigitalProduct("D1", "Editor", 59.0, -1, self.supplier, 850.0)
        with self.assertRaises(ValueError):
            DigitalProduct("D1", "Editor", 0.0, 5, self.supplier, 850.0)
        editor = DigitalProduct("D1", "Editor", 59.0, 5, self.supplier, 850.0)
        with self.assertRaises(ValueError):
            editor.update_stock(-3)

    def test_negative_weight_and_download_size_rejected(self):
        with self.assertRaises(ValueError):
            PhysicalProduct("P1", "Lamp", 25.0, 1, self.supplier, -1.0)
        with self.assertRaises(ValueError):
            DigitalProduct("D1", "Editor", 59.0, 1, self.supplier, -1.0)


class TestOrderLineValidation(unittest.TestCase):

    def setUp(self):
        supplier = Supplier("S1", "TechWorld", "sales@techworld.example")
        self.lamp = PhysicalProduct("P1", "Lamp", 25.0, 10, supplier, 1.0)

    def test_order_line_protects_its_own_quantity(self):
        for bad in (0, -2, 1.5, "3"):
            with self.subTest(quantity=bad), self.assertRaises(ValueError):
                OrderLine(self.lamp, bad)

    def test_order_rejects_invalid_quantity_and_adds_nothing(self):
        order = Order("O1")
        with self.assertRaises(ValueError) as context:
            order.add_order_line(self.lamp, 0)
        self.assertIn("greater than zero", str(context.exception))
        self.assertEqual(order.get_order_lines(), ())

    def test_valid_quantity_accepted(self):
        order = Order("O1")
        order.add_order_line(self.lamp, 3)
        self.assertAlmostEqual(order.calculate_total(), 75.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
