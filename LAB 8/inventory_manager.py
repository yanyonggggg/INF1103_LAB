import json
import os

from supplier import Supplier
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order

INVENTORY_FILE = "inventory.json"


# ---------- Building objects from saved data ----------

def supplier_from_dict(item: dict) -> Supplier:
    return Supplier(item["id"], item["name"], item["email"])


def product_from_dict(item: dict, suppliers: dict[str, Supplier]) -> Product:
    # Uses the saved "type" identifier to rebuild the correct subclass, and
    # the saved supplier ID to reconnect the association to the right Supplier.
    supplier = suppliers.get(item.get("supplier_id"))
    if supplier is None:
        raise ValueError(f"Unknown supplier '{item.get('supplier_id')}' for {item.get('id')}")

    product_type = item.get("type")
    if product_type == "physical":
        return PhysicalProduct(item["id"], item["name"], item["price"],
                               item["stock"], supplier, item["weight"])
    if product_type == "digital":
        return DigitalProduct(item["id"], item["name"], item["price"],
                              item["stock"], supplier, item["download_size"])
    raise ValueError(f"Unknown product type '{product_type}' for {item.get('id')}")


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
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, suppliers["S001"], 2.0))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.50, 40, suppliers["S001"], 0.1))
    inventory.add_product(PhysicalProduct("P003", "Guitar", 450.00, 5, suppliers["S002"], 3.5))
    inventory.add_product(DigitalProduct("D001", "Operating System", 139.99, 100, suppliers["S003"], 5200.0))
    inventory.add_product(DigitalProduct("D002", "Photo Editor", 59.00, 50, suppliers["S003"], 850.0))
    return inventory


def load_data() -> tuple[Inventory, dict[str, Supplier]]:
    # Loads inventory.json into Suppliers and an Inventory of Products.
    if not os.path.exists(INVENTORY_FILE):
        print("No existing inventory file found. Initializing standard inventory...")
        suppliers = default_suppliers()
        return default_inventory(suppliers), suppliers

    try:
        with open(INVENTORY_FILE, "r") as file:
            data = json.load(file)
        suppliers: dict[str, Supplier] = {}
        for item in data["suppliers"]:
            supplier = supplier_from_dict(item)
            suppliers[supplier.get_supplier_id()] = supplier
        inventory = Inventory()
        for item in data["products"]:
            inventory.add_product(product_from_dict(item, suppliers))
        print(f"{INVENTORY_FILE} found.")
        print("Inventory loaded successfully.\n")
        return inventory, suppliers
    except Exception as e:
        print(f"Error loading {INVENTORY_FILE}: {e}. Starting with default inventory.\n")
        suppliers = default_suppliers()
        return default_inventory(suppliers), suppliers


def save_data(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    try:
        data = {
            "suppliers": [supplier.to_dict() for supplier in suppliers.values()],
            "products": [product.to_dict() for product in inventory.products],
        }
        with open(INVENTORY_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print("Inventory saved successfully.")
    except Exception as e:
        print(f"Error saving inventory: {e}")


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


def add_product_menu(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    print("1. Physical Product")
    print("2. Digital Product")
    product_type = input("Choose product type: ").strip()
    if product_type not in ("1", "2"):
        print("ERROR! Please choose 1 or 2.")
        return

    prod_id = input("Product ID: ").strip()
    if inventory.find_product(prod_id) is not None:
        print("ERROR! Product ID already exists.")
        return

    name = input("Product Name: ").strip()

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        if product_type == "1":
            extra = float(input("Weight (kg): "))
        else:
            extra = float(input("Download Size (MB): "))
    except ValueError:
        print("ERROR! Invalid numerical input.")
        return

    if price < 0 or stock < 0 or extra < 0:
        print("ERROR! Values must be non-negative.")
        return

    supplier = choose_supplier(suppliers)
    if supplier is None:
        return

    if product_type == "1":
        product = PhysicalProduct(prod_id, name, price, stock, supplier, extra)
    else:
        product = DigitalProduct(prod_id, name, price, stock, supplier, extra)

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

    try:
        new_stock = int(input("New Stock Quantity: "))
    except ValueError:
        print("ERROR! Please enter a valid integer quantity.")
        return

    # Same call for every product type - no subclass checks needed (LSP).
    if product.update_stock(new_stock):
        print("Stock updated successfully!")
    else:
        print("ERROR! Stock quantity cannot be negative.")


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
    order = Order(f"O{order_count:03d}")
    print(f"\nCreate Order {order.get_order_id()} (leave Product ID blank to finish)")

    while True:
        prod_id = input("Product ID: ").strip()
        if not prod_id:
            break
        product = inventory.find_product(prod_id)
        if product is None:
            print("Product not found.")
            continue
        try:
            quantity = int(input("Quantity: "))
            # The Order builds the OrderLine itself from the Product + quantity.
            order.add_order_line(product, quantity)
            print(f"Added {quantity} x {product.get_name()}.")
        except ValueError:
            print("ERROR! Quantity must be a positive whole number.")

    order.display_order()


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
        print("7. Save Inventory")
        print("8. Exit")

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
            print("\nSaving inventory...")
            save_data(inventory, suppliers)
        elif choice == "8":
            print("\nSaving inventory before exit...")
            save_data(inventory, suppliers)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option! Please enter a choice between 1 and 8.")


if __name__ == "__main__":
    main()
