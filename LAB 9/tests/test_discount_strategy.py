"""Section 2 / 7: Strategy pattern for order discounts."""
import ast
import inspect
import io
import textwrap
import unittest
from contextlib import redirect_stdout

from discount_strategy import (DiscountStrategy, NoDiscount, PercentageDiscount,
                               BulkDiscount, StudentDiscount)
from order import Order
from physical_product import PhysicalProduct
from supplier import Supplier


def make_order_totalling_250(discount: DiscountStrategy | None = None) -> Order:
    supplier = Supplier("S1", "TechWorld", "sales@techworld.example")
    chair = PhysicalProduct("P1", "Chair", 100.00, 10, supplier, 7.0)
    lamp = PhysicalProduct("P2", "Lamp", 25.00, 10, supplier, 1.0)
    order = Order("O1", discount)
    order.add_order_line(chair, 2)   # 200.00
    order.add_order_line(lamp, 2)    #  50.00
    return order


class TestStrategies(unittest.TestCase):

    def test_discount_strategy_is_abstract(self):
        with self.assertRaises(TypeError):
            DiscountStrategy()

    def test_every_strategy_is_a_discount_strategy(self):
        for strategy in (NoDiscount(), PercentageDiscount(10),
                         BulkDiscount(200, 20), StudentDiscount()):
            with self.subTest(strategy=type(strategy).__name__):
                self.assertIsInstance(strategy, DiscountStrategy)

    def test_no_discount_returns_total_unchanged(self):
        self.assertEqual(NoDiscount().apply(250.0), 250.0)

    def test_percentage_discount(self):
        self.assertAlmostEqual(PercentageDiscount(10).apply(250.0), 225.0)
        self.assertAlmostEqual(PercentageDiscount(0).apply(80.0), 80.0)
        self.assertAlmostEqual(PercentageDiscount(100).apply(80.0), 0.0)

    def test_percentage_out_of_range_rejected(self):
        for bad in (-1, 101):
            with self.subTest(percentage=bad), self.assertRaises(ValueError):
                PercentageDiscount(bad)

    def test_bulk_discount_applies_at_or_above_threshold(self):
        bulk = BulkDiscount(200, 20)
        self.assertAlmostEqual(bulk.apply(250.0), 230.0)
        self.assertAlmostEqual(bulk.apply(200.0), 180.0)   # exactly the threshold
        self.assertAlmostEqual(bulk.apply(199.99), 199.99)  # just below

    def test_bulk_discount_never_goes_below_zero(self):
        self.assertEqual(BulkDiscount(0, 50).apply(30.0), 0.0)

    def test_bulk_negative_values_rejected(self):
        with self.assertRaises(ValueError):
            BulkDiscount(-1, 20)
        with self.assertRaises(ValueError):
            BulkDiscount(200, -5)

    def test_student_discount_is_five_percent(self):
        self.assertAlmostEqual(StudentDiscount().apply(200.0), 190.0)


class TestOrderUsesStrategy(unittest.TestCase):

    def test_default_strategy_is_no_discount(self):
        order = make_order_totalling_250()
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_strategy_given_when_created(self):
        order = make_order_totalling_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_subtotal(), 250.0)
        self.assertAlmostEqual(order.calculate_total(), 230.0)

    def test_set_discount_changes_strategy_on_existing_order(self):
        # Predict first 2.3: 230.0 with BulkDiscount, then 225.0 with 10%.
        order = make_order_totalling_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_total(), 230.0)
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225.0)
        self.assertAlmostEqual(order.calculate_subtotal(), 250.0)  # lines unchanged

    def test_new_strategy_works_without_changing_order(self):
        # A brand-new strategy written here, after Order was finished.
        class HalfPrice(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        order = make_order_totalling_250(HalfPrice())
        self.assertAlmostEqual(order.calculate_total(), 125.0)

    def test_two_orders_can_share_one_strategy_object(self):
        shared = PercentageDiscount(10)
        order_1 = make_order_totalling_250(shared)
        order_2 = make_order_totalling_250(shared)
        self.assertIs(order_1.get_discount(), order_2.get_discount())
        self.assertAlmostEqual(order_1.calculate_total(), order_2.calculate_total())

    def test_display_shows_subtotal_discount_and_total(self):
        order = make_order_totalling_250(BulkDiscount(200, 20))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            order.display_order()
        output = buffer.getvalue()
        self.assertIn("Subtotal", output)
        self.assertIn("$20 off orders of $200 or more", output)
        self.assertIn("$   230.00", output)


class TestOrderHasNoDiscountLogic(unittest.TestCase):
    """Order must not contain if/elif logic about discount types."""

    def test_calculate_total_has_no_branches(self):
        tree = ast.parse(textwrap.dedent(inspect.getsource(Order.calculate_total)))
        branches = [node for node in ast.walk(tree) if isinstance(node, (ast.If, ast.IfExp))]
        self.assertEqual(branches, [])

    def test_order_does_not_know_concrete_discounts(self):
        source = inspect.getsource(Order)
        for name in ("PercentageDiscount", "BulkDiscount", "StudentDiscount", "discount_type"):
            with self.subTest(name=name):
                self.assertNotIn(name, source)

    def test_type_hints_use_the_abstract_strategy(self):
        hints = inspect.get_annotations(Order.__init__, eval_str=True)
        self.assertEqual(hints["discount"], DiscountStrategy | None)
        hints = inspect.get_annotations(Order.set_discount, eval_str=True)
        self.assertIs(hints["discount"], DiscountStrategy)
        hints = inspect.get_annotations(DiscountStrategy.apply, eval_str=True)
        self.assertIs(hints["total"], float)
        self.assertIs(hints["return"], float)


if __name__ == "__main__":
    unittest.main(verbosity=2)
