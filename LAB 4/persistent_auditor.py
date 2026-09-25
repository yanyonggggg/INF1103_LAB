import os # Importing the os module to check for file existence

def load_inventory():
    # Reads previously saved information from the inventory file.
    # Starts with an empty inventory without error if the file does not exist.
    inventory = 0
    history = []
    
    if os.path.exists("inventory.txt"): # Checks if file path exists
        try:
            with open("inventory.txt", "r") as file:
                lines = file.readlines() # Reads lines from file and return as string
                if len(lines) >= 1:
                    inventory = int(lines[0].strip()) # Splits the string into list of integers
                if len(lines) >= 2:
                    history_str = lines[1].strip()
                    if history_str:
                        history = [int(x) for x in history_str.split(",")] 
        except Exception:
            # Failsafe to ensure the program continues running without producing an error
            pass
            
    return inventory, history


def save_inventory(total, history):
    # Saves the final total and transaction history list to inventory.txt.
    with open("inventory.txt", "w") as file: # Opens the file and write, if does not exist, creates a new file
        file.write(f"{total}\n")
        
        # Convert history list to a comma-separated string for easy storage
        history_str = ",".join(str(item) for item in history)
        file.write(f"{history_str}\n")
    print("Data successfully saved to inventory.txt")


def get_valid_input():
    # Handles prompt and input validation.
    # Returns an integer delivery amount, or the string 'quit'.
    # Returns None for invalid inputs.
    user_input = input("Enter stock quantity or 'quit': ").strip()
    
    if user_input.lower() == "quit":
        return "quit"
    
    try:
        val = int(user_input)
        if val < 0:
            print("ERROR! Please enter a positive integer.")
            return None
        return val
    except ValueError:
        print("ERROR! Please enter a valid integer or 'quit' to exit.")
        return None


def process_delivery(current_total, new_value):
    # Calculates and returns the new inventory total.
    return current_total + new_value

def calculate_tax(amount):

    # Calculates 10% tax for a specific delivery amount.
    return amount * 0.10


def generate_report(total_units, failed_attempts, history):
    # Prints the final summary report upon exiting.
    print("\n--- Final Inventory Report ---")
    print(f"Total Deliveries Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")
    print(f"Transaction History: {history}")


def main():
    # Initialize inventory and history from file instead of starting at 0
    inventory, history = load_inventory()
    failed_attempts = 0

    while True:
        # Check maximum inventory threshold (500 units limit from Week 2 logic)
        if inventory >= 501:
            print("ALERT! Total inventory cannot exceed 500 units. Exiting program.")
            save_inventory(inventory, history)
            break

        result = get_valid_input()

        if result == "quit":
            print("Exiting program.")
            save_inventory(inventory, history)
            break
        elif result is None:
            failed_attempts += 1
            continue

        # Valid input processed using pure functions
        delivery_amount = result
        tax = calculate_tax(delivery_amount)
        inventory = process_delivery(inventory, delivery_amount)
        
        # Track the valid transaction amount in the history list
        history.append(delivery_amount)


        print(f"Delivery Added: {delivery_amount} (Tax: {tax:.2f})")
        print(f"Current Total Inventory: {inventory}\n")

    generate_report(inventory, failed_attempts, history)


if __name__ == "__main__":
    main()