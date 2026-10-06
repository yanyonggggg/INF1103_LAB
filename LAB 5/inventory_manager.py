import json
import os

INVENTORY_FILE = "inventory.json"


def load_inventory():
    """Checks whether inventory.json exists and loads it.
    
    Otherwise, initializes with default sample data or an empty list.
    """
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