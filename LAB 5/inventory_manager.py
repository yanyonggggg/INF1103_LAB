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

    name = input("Product Name: ").strip()
    
    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        if price < 0 or stock < 0:
            print("ERROR! Price and stock must be non-negative values.")
            return
    except ValueError:
        print("ERROR! Invalid numerical input for price or stock.")
        return

    new_product = {
        "id": prod_id,
        "name": name,
        "price": price,
        "stock": stock
    }
    inventory.append(new_product)
    print("Product added successfully!")

def update_stock(inventory):
    # Updates stock quantity for a given product ID.
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID: ").strip()
    
    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("\nProduct Found:")
            print(f"Name: {item['name']}")
            print(f"Current Stock: {item['stock']}\n")
            
            try:
                new_stock = int(input("New Stock Quantity: "))
                if new_stock < 0:
                    print("ERROR! Stock quantity cannot be negative.")
                    return
                item["stock"] = new_stock
                print("Stock updated successfully!")
                return
            except ValueError:
                print("ERROR! Please enter a valid integer quantity.")
                return
                
    print("Product not found.")


def search_product(inventory):
    # Searches for a product by its ID.
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()
    
    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("\nProduct Found")
            print("-" * 40)
            print(f"ID: {item['id']}")
            print(f"Name: {item['name']}")
            print(f"Price: ${item['price']:.2f}")
            print(f"Stock: {item['stock']}")
            print("-" * 40)
            return
            
    print("\nProduct not found.")
    

def search_product(inventory):
    """Searches for a product by its ID."""
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()
    
    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("\nProduct Found")
            print("-" * 40)
            print(f"ID: {item['id']}")
            print(f"Name: {item['name']}")
            print(f"Price: ${item['price']:.2f}")
            print(f"Stock: {item['stock']}")
            print("-" * 40)
            return
            
    print("\nProduct not found.")


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
            display_all(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
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