import csv
import json

from supplier import Supplier
from product import Product
from product_factory import ProductFactory
from inventory import Inventory
from order import Order
from discount_strategy import (DiscountStrategy, NoDiscount, PercentageDiscount,
                               BulkDiscount, StudentDiscount)

INVENTORY_FILE = "inventory.json"
PRODUCTS_FILE = "products.csv"

# Menu choices mapped to objects, so the menu needs no if/elif to pick one.
PRODUCT_TYPES: dict[str, str] = {"1": "physical", "2": "digital"}

# The same strategy objects are shared by every order that picks them
# (association: an Order uses a strategy, it does not own it).
DISCOUNT_OPTIONS: dict[str, DiscountStrategy] = {
    "1": NoDiscount(),
    "2": PercentageDiscount(10),
    "3": BulkDiscount(200, 20),
    "4": StudentDiscount(),
}


# ---------- Building objects from saved data ----------

def supplier_from_dict(item: dict) -> Supplier:
    return Supplier(item["id"], item["name"], item["email"])


def product_from_dict(item: dict, suppliers: dict[str, Supplier]) -> Product:
    # Uses the saved supplier ID to reconnect the association to the right
    # Supplier, then asks the factory to build the right Product subclass.
    supplier = suppliers.get(item.get("supplier_id"))
    if supplier is None:
        raise ValueError(f"Unknown supplier '{item.get('supplier_id')}' for {item.get('id')}")
    return ProductFactory.create(item.get("type"), item["id"], item["name"],
                                 item["price"], item["stock"], supplier,
                                 weight=item.get("weight", 0.0),
                                 download_size=item.get("download_size", 0.0))


# ---------- File handling ----------

def default_suppliers() -> dict[str, Supplier]:
    # Suppliers are created on their own, before any Product refers to them.
    suppliers = [
        Supplier("S001", "TechWorld Distributors", "sales@techworld.example"),
        Supplier("S002", "Melody Music Supply", "orders@melodymusic.example"),
        Supplier("S003", "SoftKey Licensing", "licences@softkey.example"),
    ]
    return {supplier.get_supplier_id(): supplier for supplier in suppliers}


def default_inventory(suppliers: dict[str, Supplier]) -> Inventory:
    # Every product is created through the factory, not directly.
    inventory = Inventory()
    inventory.add_product(ProductFactory.create("physical", "P001", "Laptop", 1200.00, 15,
                                                suppliers["S001"], weight=2.0))
    inventory.add_product(ProductFactory.create("physical", "P002", "Mouse", 25.50, 40,
                                                suppliers["S001"], weight=0.1))
    inventory.add_product(ProductFactory.create("physical", "P003", "Guitar", 450.00, 5,
                                                suppliers["S002"], weight=3.5))
    inventory.add_product(ProductFactory.create("digital", "D001", "Operating System", 139.99, 100,
                                                suppliers["S003"], download_size=5200.0))
    inventory.add_product(ProductFactory.create("digital", "D002", "Photo Editor", 59.00, 50,
                                                suppliers["S003"], download_size=850.0))
    return inventory


def load_data() -> tuple[Inventory, dict[str, Supplier]]:
    # Loads inventory.json into Suppliers and an Inventory of Products.
    try:
        file = open(INVENTORY_FILE, "r", encoding="utf-8")
    except FileNotFoundError:
        print("No existing inventory file found. Initializing standard inventory...")
        suppliers = default_suppliers()
        return default_inventory(suppliers), suppliers

    with file:
        try:
            data = json.load(file)
            suppliers: dict[str, Supplier] = {}
            for item in data["suppliers"]:
                supplier = supplier_from_dict(item)
                suppliers[supplier.get_supplier_id()] = supplier
            inventory = Inventory()
            for item in data["products"]:
                inventory.add_product(product_from_dict(item, suppliers))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            # Expected problems with a damaged or hand-edited file: invalid
            # JSON, a missing field, wrong structure, or data that breaks a
            # validation rule. The saved file is all-or-nothing, so fall back.
            print(f"Error loading {INVENTORY_FILE}: {error}. Starting with default inventory.\n")
            suppliers = default_suppliers()
            return default_inventory(suppliers), suppliers

    print(f"{INVENTORY_FILE} found.")
    print("Inventory loaded successfully.\n")
    return inventory, suppliers


def save_data(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    data = {
        "suppliers": [supplier.to_dict() for supplier in suppliers.values()],
        "products": [product.to_dict() for product in inventory.products],
    }
    try:
        with open(INVENTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        # e.g. no permission to write, or the disk is full.
        print(f"Error saving inventory: {error}")
    else:
        print("Inventory saved successfully.")


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    """Read products from a CSV file, build each one through ProductFactory
    and add it to the inventory.

    Expected columns: product_type,product_id,name,price,stock_quantity
    A bad row is reported and skipped; the remaining rows still load.
    """
    try:
        file = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for row in reader:
                if not row:
                    continue  # ignore blank lines
                line_number = reader.line_num  # line in the file, header = 1
                try:
                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(product_type, product_id, name,
                                                    float(price), int(stock), supplier)
                except ValueError as error:
                    # Unknown type, a value that is not a number, a broken
                    # validation rule, or the wrong number of columns.
                    print(f"Line {line_number} skipped: {error}")
                    continue
                if inventory.add_product(product):
                    loaded += 1
                else:
                    print(f"Line {line_number} skipped: product ID {product_id} already exists.")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")


# ---------- Input helpers: keep asking until the value is valid ----------

def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_whole_number(prompt: str, minimum: int = 0) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                print(f"Please enter a whole number of {minimum} or more.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number, e.g. 5")


# ---------- Menu actions (user input lives here, not in the classes) ----------

def display_suppliers(suppliers: dict[str, Supplier]) -> None:
    print("\nSuppliers")
    for supplier in suppliers.values():
        supplier.display_information()


def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier | None:
    display_suppliers(suppliers)
    supplier_id = input("Supplier ID (or N for a new supplier): ").strip().upper()
    if supplier_id == "N":
        new_id = input("New Supplier ID: ").strip().upper()
        if not new_id or new_id in suppliers:
            print("ERROR! Supplier ID is empty or already exists.")
            return None
        name = input("Supplier Name: ").strip()
        email = input("Contact Email: ").strip()
        supplier = Supplier(new_id, name, email)
        suppliers[new_id] = supplier
        return supplier

    supplier = suppliers.get(supplier_id)
    if supplier is None:
        print("ERROR! Supplier not found.")
    return supplier


def choose_discount() -> DiscountStrategy:
    print("\nDiscount options")
    for key, strategy in DISCOUNT_OPTIONS.items():
        print(f"{key}. {strategy}")
    while True:
        choice = input("Choose discount: ").strip()
        if choice in DISCOUNT_OPTIONS:
            return DISCOUNT_OPTIONS[choice]
        print(f"Please choose a number from 1 to {len(DISCOUNT_OPTIONS)}.")


def add_product_menu(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    print("1. Physical Product")
    print("2. Digital Product")
    product_type = PRODUCT_TYPES.get(input("Choose product type: ").strip())
    if product_type is None:
        print("ERROR! Please choose 1 or 2.")
        return

    prod_id = input("Product ID: ").strip()
    if not prod_id or inventory.find_product(prod_id) is not None:
        print("ERROR! Product ID is empty or already exists.")
        return

    name = input("Product Name: ").strip()
    price = get_positive_float("Price: ")
    stock = get_whole_number("Stock Quantity: ", minimum=0)
    weight = download_size = 0.0
    if product_type == "physical":
        weight = get_positive_float("Weight (kg): ")
    else:
        download_size = get_positive_float("Download Size (MB): ")

    supplier = choose_supplier(suppliers)
    if supplier is None:
        return

    # The menu never names PhysicalProduct or DigitalProduct - the factory decides.
    product = ProductFactory.create(product_type, prod_id, name, price, stock, supplier,
                                    weight=weight, download_size=download_size)
    inventory.add_product(product)
    print("Product added successfully!")


def update_stock_menu(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.find_product(prod_id)
    if product is None:
        print("Product not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}\n")

    # Same call for every product type - no subclass checks needed (LSP).
    product.update_stock(get_whole_number("New Stock Quantity: ", minimum=0))
    print("Stock updated successfully!")


def search_product_menu(inventory: Inventory) -> None:
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.find_product(prod_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 40)
    product.display_information()
    print(f"    Fulfilment: {product.get_fulfilment_info()}")
    print("    ", end="")
    product.get_supplier().display_information()
    print("-" * 40)


def create_order_menu(inventory: Inventory, order_count: int) -> None:
    order = Order(f"O{order_count:03d}")  # starts with NoDiscount()
    print(f"\nCreate Order {order.get_order_id()} (leave Product ID blank to finish)")

    while True:
        prod_id = input("Product ID: ").strip()
        if not prod_id:
            break
        product = inventory.find_product(prod_id)
        if product is None:
            print("Product not found.")
            continue
        quantity = get_whole_number("Quantity: ", minimum=1)
        # The Order builds the OrderLine itself from the Product + quantity.
        order.add_order_line(product, quantity)
        print(f"Added {quantity} x {product.get_name()}.")

    if order.get_order_lines():
        print(f"Subtotal: ${order.calculate_subtotal():.2f}")
        # Strategy pattern: swap the discount behaviour without changing Order.
        order.set_discount(choose_discount())
    order.display_order()


def import_products_menu(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nImport Products from CSV")
    path = input(f"CSV file (blank for {PRODUCTS_FILE}): ").strip() or PRODUCTS_FILE
    print("Which supplier provides these products?")
    supplier = choose_supplier(suppliers)
    if supplier is None:
        return
    load_products(path, inventory, supplier)


def main() -> None:
    print("INVENTORY MANAGEMENT SYSTEM")
    inventory, suppliers = load_data()
    order_count = 0

    while True:
        print("\nMENU")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. View Suppliers")
        print("6. Create Order")
        print("7. Import Products from CSV")
        print("8. Save Inventory")
        print("9. Exit")

        choice = input("Enter option: ").strip()

        if choice == "1":
            inventory.display_all_products()
        elif choice == "2":
            add_product_menu(inventory, suppliers)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            display_suppliers(suppliers)
        elif choice == "6":
            order_count += 1
            create_order_menu(inventory, order_count)
        elif choice == "7":
            import_products_menu(inventory, suppliers)
        elif choice == "8":
            print("\nSaving inventory...")
            save_data(inventory, suppliers)
        elif choice == "9":
            print("\nSaving inventory before exit...")
            save_data(inventory, suppliers)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option! Please enter a choice between 1 and 9.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        # Input stream closed (e.g. docker run without -it) or Ctrl+C.
        print("\nInput ended. Program closed without saving.")
