import json
import os

from product import Product
from inventory import Inventory

INVENTORY_FILE = "inventory.json"


# ---------- File handling ----------

def load_inventory():
    # Loads inventory.json into an Inventory of Product objects.
    inventory = Inventory()

    if os.path.exists(INVENTORY_FILE):
        try:
            with open(INVENTORY_FILE, "r") as file:
                data = json.load(file)
            for item in data:
                inventory.add_product(
                    Product(item["id"], item["name"], item["price"], item["stock"])
                )
            print(f"{INVENTORY_FILE} found.")
            print("Inventory loaded successfully.\n")
            return inventory
        except Exception as e:
            print(f"Error loading {INVENTORY_FILE}: {e}. Starting with default inventory.\n")
            inventory = Inventory()
    else:
        print("No existing inventory file found. Initializing standard inventory...")

    inventory.add_product(Product("P001", "Laptop", 1200.00, 15))
    inventory.add_product(Product("P002", "Mouse", 25.50, 40))
    inventory.add_product(Product("P003", "Keyboard", 45.00, 25))
    return inventory


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
    prod_id = input("Product ID: ").strip()

    if inventory.search_product(prod_id) is not None:
        print("ERROR! Product ID already exists.")
        return

    name = input("Product Name: ").strip()

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
    except ValueError:
        print("ERROR! Invalid numerical input for price or stock.")
        return

    if price < 0 or stock < 0:
        print("ERROR! Price and stock must be non-negative values.")
        return

    inventory.add_product(Product(prod_id, name, price, stock))
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