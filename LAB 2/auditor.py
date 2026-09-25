inventory = 0
failed_attempts = 0

def check_if_int(value):
    try:
        int(value)
        if int(value) < 0:
            print("ERROR! Please enter a positive integer.")
            return False
        return True
    except ValueError:
        return False    

    
def quit(value):
    try:
        if value == "quit":
            return True
    except ValueError:
        return False

def check_stock_quantity(value):
    if value < 501:
        return True
    else:
        print("ALERT! Total inventory cannnot exceed 500 units. Exiting program.")
        return False

while True:
    over_500 = check_stock_quantity(inventory)
    if over_500 == False:
        break

    stock_quantity = input("Enter stock quantity or 'quit': ")
    if quit(stock_quantity) == True:
        print("Exiting program.")
        print("Total Units Processed: ", inventory) 
        print("Total Failed Attempts: ", failed_attempts)
        break

    checkint = check_if_int(stock_quantity)
    if checkint == True:
            inventory = inventory + int(stock_quantity)
            print("Inventory: ",inventory)
            
    else:
        print("ERROR! Please enter a valid integer or 'quit' to exit.")
        failed_attempts += 1
        continue

