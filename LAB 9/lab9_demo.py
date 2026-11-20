"""Lab 9 walkthrough: runs each "Predict first" scenario and prints the result.

Run with:  python lab9_demo.py
Compare each section's output with the prediction written down beforehand.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

from discount_strategy import (DiscountStrategy, BulkDiscount, PercentageDiscount,
                               StudentDiscount)
from inventory import Inventory
from inventory_manager import get_positive_float, load_products
from order import Order
from product_factory import ProductFactory
from supplier import Supplier

HERE = os.path.dirname(os.path.abspath(__file__))


def heading(title: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ---------------------------------------------------------------- Section 2
def demo_strategy() -> None:
    heading("2.3 STRATEGY: same order, different discount strategies")

    supplier = Supplier("S001", "TechWorld Distributors", "sales@techworld.example")
    chair = ProductFactory.create("physical", "P100", "Office Chair", 100.00, 10, supplier, weight=7.0)
    lamp = ProductFactory.create("physical", "P101", "Desk Lamp", 25.00, 20, supplier, weight=1.0)

    order = Order("O001", BulkDiscount(200, 20))
    order.add_order_line(chair, 2)   # 200.00
    order.add_order_line(lamp, 2)    #  50.00  -> lines add up to 250.00

    print(f"Order lines add up to: {order.calculate_subtotal():.2f}")
    print(f"BulkDiscount(200, 20)        -> calculate_total() = {order.calculate_total()}")
    order.set_discount(PercentageDiscount(10))
    print(f"set_discount(PercentageDiscount(10)) -> calculate_total() = {order.calculate_total()}")
    order.display_order()

    heading("2.4 EXTEND WITHOUT MODIFYING: StudentDiscount added, Order unchanged")
    order.set_discount(StudentDiscount())
    print(f"StudentDiscount() -> calculate_total() = {order.calculate_total()}")

    class HalfPrice(DiscountStrategy):
        # Written here, after Order was finished. Order still works with it.
        def apply(self, total: float) -> float:
            return total / 2

    order.set_discount(HalfPrice())
    print(f"HalfPrice() (defined in this demo) -> calculate_total() = {order.calculate_total()}")

    heading("2.4 RELATIONSHIP: can two orders share one strategy object?")
    shared = PercentageDiscount(10)
    order_a = Order("O002", shared)
    order_b = Order("O003", shared)
    order_a.add_order_line(chair, 1)
    order_b.add_order_line(lamp, 2)
    print(f"order_a.get_discount() is order_b.get_discount(): "
          f"{order_a.get_discount() is order_b.get_discount()}")
    print(f"order_a total: {order_a.calculate_total():.2f} | order_b total: {order_b.calculate_total():.2f}")
    del order_a
    print(f"After 'del order_a' the shared strategy still works: {shared.apply(100.0)}")


# ---------------------------------------------------------------- Section 3
def demo_factory() -> None:
    heading("3.2 FACTORY: ProductFactory.create(\"service\", ...) with nothing catching it")

    # Run it in a separate Python process so the uncaught exception really
    # crashes *that* program, and we can show what happened to it.
    code = (
        "from product_factory import ProductFactory\n"
        "from supplier import Supplier\n"
        "supplier = Supplier('S1', 'TechWorld', 'sales@techworld.example')\n"
        "print('Before create()')\n"
        "ProductFactory.create('service', 'S001', 'Installation', 30.0, 5, supplier)\n"
        "print('After create()')\n"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=HERE,
                            capture_output=True, text=True)
    print("--- stdout ---")
    print(result.stdout, end="")
    print("--- stderr ---")
    print(result.stderr.replace(HERE + os.sep, ""), end="")  # shorter file paths
    print(f"--- exit code: {result.returncode} ---")

    heading("3.3 FACTORY returns the Product type")
    supplier = Supplier("S003", "SoftKey Licensing", "licences@softkey.example")
    for product_type in ("physical", "digital"):
        product = ProductFactory.create(product_type, f"{product_type[0].upper()}900",
                                        f"Sample {product_type}", 10.0, 1, supplier)
        print(f"create({product_type!r}) -> {type(product).__name__}: "
              f"{product.get_fulfilment_info()}")


# ---------------------------------------------------------------- Section 4
def demo_validation() -> None:
    heading("4. VALIDATION: rules enforced by the class that owns them")
    supplier = Supplier("S001", "TechWorld Distributors", "sales@techworld.example")
    attempts = [
        ("Physical product with price 0",
         lambda: ProductFactory.create("physical", "P1", "Lamp", 0.0, 10, supplier)),
        ("Physical product with stock -1",
         lambda: ProductFactory.create("physical", "P1", "Lamp", 25.0, -1, supplier)),
        ("Digital product with stock -1 (LSP)",
         lambda: ProductFactory.create("digital", "D1", "Editor", 59.0, -1, supplier)),
        ("OrderLine with quantity 0",
         lambda: Order("O1").add_order_line(
             ProductFactory.create("physical", "P1", "Lamp", 25.0, 10, supplier), 0)),
    ]
    for label, attempt in attempts:
        try:
            attempt()
            print(f"{label:<38} -> accepted (unexpected!)")
        except ValueError as error:
            print(f"{label:<38} -> ValueError: {error}")

    editor = ProductFactory.create("digital", "D1", "Editor", 59.0, 5, supplier)
    try:
        editor.update_stock(-3)
    except ValueError as error:
        print(f"{'DigitalProduct.update_stock(-3)':<38} -> ValueError: {error}")
    print(f"Editor stock is still {editor.get_stock()}")


# ---------------------------------------------------------------- Section 5
def demo_user_input() -> None:
    heading("5.1 USER INPUT: user types abc, then -5, then 12.50")
    typed = iter(["abc", "-5", "12.50"])

    def fake_input(prompt: str) -> str:
        value = next(typed)
        print(f"{prompt}{value}")  # echo what the user "typed"
        return value

    with patch("builtins.input", fake_input):
        value = get_positive_float("Enter price: ")
    print(f"Returned value: {value!r}")


def demo_load_products() -> None:
    heading("5.2 LOAD PRODUCTS: products.csv")
    supplier = Supplier("S005", "Office Supplies Co", "orders@office.example")
    inventory = Inventory("CSV import")
    load_products(os.path.join(HERE, "products.csv"), inventory, supplier)
    inventory.display_all_products()

    heading("5.2 LOAD PRODUCTS: products.csv renamed (file missing)")
    # Work on a copy in a temporary folder so the real products.csv is untouched.
    original_folder = os.getcwd()
    with tempfile.TemporaryDirectory() as folder:
        shutil.copy(os.path.join(HERE, "products.csv"),
                    os.path.join(folder, "products_old.csv"))  # the "renamed" file
        os.chdir(folder)
        try:
            load_products("products.csv", Inventory(), supplier)
        finally:
            os.chdir(original_folder)


if __name__ == "__main__":
    demo_strategy()
    demo_factory()
    demo_validation()
    demo_user_input()
    demo_load_products()
