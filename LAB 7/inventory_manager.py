import json
import os

from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from inventory import Inventory

INVENTORY_FILE = "inventory.json"


# ---------- Building products from saved data ----------

def product_from_dict(item):
    # Uses the saved "type" identifier to rebuild the correct subclass.
    product_type = item.get("type")
    if product_type == "physical":
        return PhysicalProduct(item["id"], item["name"], item["price"],
                               item["stock"], item["weight"])
    if product_type == "digital":
        return DigitalProduct(item["id"], item["name"], item["price"],
                              item["stock"], item["download_size"])
    raise ValueError(f"Unknown product type '{product_type}' for {item.get('id')}")


# ---------- File handling ----------

def default_inventory():
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, 2.0))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.50, 40, 0.1))
    inventory.add_product(PhysicalProduct("P003", "Guitar", 450.00, 5, 3.5))
    inventory.add_product(DigitalProduct("D001", "Operating System", 139.99, 100, 5200.0))
    inventory.add_product(DigitalProduct("D002", "Photo Editor", 59.00, 50, 850.0))
    return inventory


def load_inventory():
    # Loads inventory.json into an Inventory of PhysicalProduct / DigitalProduct objects.
    if not os.path.exists(INVENTORY_FILE):
        print("No existing inventory file found. Initializing standard inventory...")
        return default_inventory()

    try:
        with open(INVENTORY_FILE, "r") as file:
            data = json.load(file)
        inventory = Inventory()
        for item in data:
            inventory.add_product(product_from_dict(item))
        print(f"{INVENTORY_FILE} found.")
        print("Inventory loaded successfully.\n")
        return inventory
    except Exception as e:
        print(f"Error loading {INVENTORY_FILE}: {e}. Starting with default inventory.\n")
        return default_inventory()


def save_inventory(inventory):
    try:
        data = [product.to_dict() for product in inventory.get_products()]
        with open(INVENTORY_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print("Inventory saved successfully.")
    except Exception as e:
        print(f"Error saving inventory: {e}")


# ---------- Menu actions (user input lives here, not in the classes) ----------

def add_product_menu(inventory):
    print("\nAdd New Product")
    print("1. Physical Product")
    print("2. Digital Product")
    product_type = input("Choose product type: ").strip()
    if product_type not in ("1", "2"):
        print("ERROR! Please choose 1 or 2.")
        return

    prod_id = input("Product ID: ").strip()
    if inventory.search_product(prod_id) is not None:
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

    if product_type == "1":
        product = PhysicalProduct(prod_id, name, price, stock, extra)
    else:
        product = DigitalProduct(prod_id, name, price, stock, extra)

    inventory.add_product(product)
    print("Product added successfully!")


def update_stock_menu(inventory):
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.search_product(prod_id)
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

    if product.update_stock(new_stock):
        print("Stock updated successfully!")
    else:
        print("ERROR! Stock quantity cannot be negative.")


def search_product_menu(inventory):
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.search_product(prod_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 40)
    product.display_information()
    print(f"    Fulfilment: {product.get_fulfilment_info()}")
    print("-" * 40)


def main():
    print("INVENTORY MANAGEMENT SYSTEM")
    inventory = load_inventory()

    while True:
        print("\nMENU")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")

        choice = input("Enter option: ").strip()

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            print("\nSaving inventory...")
            save_inventory(inventory)
        elif choice == "6":
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option! Please enter a choice between 1 and 6.")


if __name__ == "__main__":
    main()
