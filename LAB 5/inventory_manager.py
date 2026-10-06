import json
import os

INVENTORY_FILE = "inventory.json"


def load_inventory():
    # Checks whether inventory.json exists and loads it.
    
    # Otherwise, initializes with default sample data or an empty list.
    
    if os.path.exists(INVENTORY_FILE):
        try:
            with open(INVENTORY_FILE, "r") as file:
                inventory = json.load(file)
                print(f"{INVENTORY_FILE} found.")
                print("Inventory loaded successfully.\n")
                return inventory
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading {INVENTORY_FILE}: {e}. Starting with default inventory.\n")
    
    # Initial data representation: list of product dictionaries
    print("No existing inventory file found. Initializing standard inventory...")
    return [
        {"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15},
        {"id": "P002", "name": "Mouse", "price": 25.50, "stock": 40},
        {"id": "P003", "name": "Keyboard", "price": 45.00, "stock": 25}
    ]


def save_inventory(inventory):
    # Saves the current inventory list to inventory.json.
    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(inventory, file, indent=4)
        print("Inventory saved successfully.")
    except Exception as e:
        print(f"Error saving inventory: {e}")


def display_all(inventory):
    # Displays all products in a structured view.
    print("\nCurrent Inventory")
    if not inventory:
        print("No products available.")
        return
    
    for item in inventory:
        print(f"ID: {item['id']} | Name: {item['name']} | Price: ${item['price']:.2f} | Stock: {item['stock']}")


def add_product(inventory):
    # Adds a new product dictionary to the inventory list.
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()
    
    # Check for existing product ID
    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("ERROR! Product ID already exists.")
            return