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


def generate_report(total_units, failed_attempts):
    
    #Prints the final summary report upon exiting.
    
    print("\n--- Final Inventory Report ---")
    print(f"Total Deliveries Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")


def main():
    inventory = 0
    failed_attempts = 0

    while True:
        # Check maximum inventory threshold (500 units limit from Week 2 logic)
        if inventory >= 501:
            print("ALERT! Total inventory cannot exceed 500 units. Exiting program.")
            break

        result = get_valid_input()

        if result == "quit":
            print("Exiting program.")
            break
        elif result is None:
            failed_attempts += 1
            continue

        # Valid input processed using pure functions
        delivery_amount = result
        tax = calculate_tax(delivery_amount)
        inventory = process_delivery(inventory, delivery_amount)

        print(f"Delivery Added: {delivery_amount} (Tax: {tax:.2f})")
        print(f"Current Total Inventory: {inventory}\n")

    generate_report(inventory, failed_attempts)


if __name__ == "__main__":
    main()