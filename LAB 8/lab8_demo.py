"""Lab 8 walkthrough: runs each section's test scenario and prints the results.

Run with:  python lab8_demo.py
(Each "Predict first" scenario prints its outcome so it can be compared
with the prediction written down beforehand.)
"""
from supplier import Supplier
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order


def heading(title: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ---------------------------------------------------------------- Section 2
def demo_association() -> None:
    heading("2. ASSOCIATION: Supplier <-> Product")

    supplier = Supplier("S100", "Melody Music Supply", "orders@melodymusic.example")
    guitar = PhysicalProduct("P100", "Guitar", 450.00, 5, supplier, 3.5)
    music_app = DigitalProduct("D100", "Music Studio App", 89.00, 30, supplier, 1200.0)

    print("Supplier created on its own, then passed into each Product:")
    guitar.display_supplier_information()
    music_app.display_supplier_information()

    print(f"\nguitar.get_supplier() is music_app.get_supplier(): "
          f"{guitar.get_supplier() is music_app.get_supplier()}  (one shared Supplier)")
    print(f"Supplier is a separate object from the products: "
          f"{supplier is not guitar and supplier is not music_app}")

    supplier_id_before = id(supplier)
    print("\nPredict first -> running: del supplier")
    del supplier
    print("Products after 'del supplier':")
    guitar.display_supplier_information()
    music_app.display_supplier_information()
    print(f"Same Supplier object as before? "
          f"{id(guitar.get_supplier()) == supplier_id_before}")
    print("-> 'del' only removed the variable name. The Products still hold a")
    print("   reference, so the Supplier object is still alive.")


# ---------------------------------------------------------------- Section 3
def demo_aggregation() -> None:
    heading("3. AGGREGATION: Inventory <>-- Product")

    supplier = Supplier("S001", "TechWorld Distributors", "sales@techworld.example")
    # Step 1: create the Product before any Inventory exists.
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.0)
    print("Step 1 - Product created before any Inventory:")
    laptop.display_information()

    # Step 2: add to Inventory A.
    warehouse_a = Inventory("Warehouse A")
    warehouse_b = Inventory("Warehouse B")
    warehouse_a.add_product(laptop)
    print("\nStep 2 - added to Warehouse A:")
    warehouse_a.display_all_products()

    # Step 3: remove from Inventory A, check it still works.
    removed = warehouse_a.remove_product("P001")
    print("\nStep 3 - removed from Warehouse A (Predict first):")
    warehouse_a.display_all_products()
    print("The removed Product still works:")
    removed.display_information()
    print(f"removed is laptop: {removed is laptop}")
    print(f"laptop.update_stock(12) -> {laptop.update_stock(12)}, "
          f"stock now {laptop.get_stock()}")

    # Step 4: add the same object to Inventory B.
    warehouse_b.add_product(laptop)
    print("\nStep 4 - same object added to Warehouse B:")
    warehouse_b.display_all_products()
    print(f"Warehouse B holds the same object: {warehouse_b.find_product('P001') is laptop}")

    # transfer_product() does remove + add in one step.
    print("\nTransfer back B -> A with transfer_product():")
    print(f"transfer_product('P001', warehouse_a) -> "
          f"{warehouse_b.transfer_product('P001', warehouse_a)}")
    print(f"In A: {warehouse_a.find_product('P001') is laptop} | "
          f"In B: {warehouse_b.find_product('P001') is not None}")

    # Emptying an inventory does not destroy its products.
    warehouse_a.clear()
    print("\nWarehouse A cleared. Product still exists and works:")
    laptop.display_information()


# ---------------------------------------------------------------- Section 4
def demo_composition() -> None:
    heading("4. COMPOSITION: Order <*>-- OrderLine")

    supplier = Supplier("S001", "TechWorld Distributors", "sales@techworld.example")
    licences = Supplier("S003", "SoftKey Licensing", "licences@softkey.example")
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.0)
    mouse = PhysicalProduct("P002", "Mouse", 25.50, 40, supplier, 0.1)
    os_product = DigitalProduct("D001", "Operating System", 139.99, 100, licences, 5200.0)

    order_1 = Order("O001")
    # The Order receives a Product + quantity and creates the OrderLine itself.
    order_1.add_order_line(laptop, 1)
    order_1.add_order_line(mouse, 2)
    order_1.add_order_line(os_product, 1)
    order_1.display_order()

    print("\nPredict first -> the same Product (laptop) added to a second Order:")
    order_2 = Order("O002")
    order_2.add_order_line(laptop, 3)
    order_2.display_order()

    line_1 = order_1.get_order_lines()[0]
    line_2 = order_2.get_order_lines()[0]
    print(f"\nOrderLine objects: id {id(line_1)} vs id {id(line_2)} -> "
          f"same object? {line_1 is line_2}")
    print(f"Product objects:   id {id(line_1.get_product())} vs id "
          f"{id(line_2.get_product())} -> same object? "
          f"{line_1.get_product() is line_2.get_product()}")
    print("-> 2 OrderLine objects (one per Order), but only 1 laptop Product.")

    print("\nRemove the mouse line through the Order:")
    print(f"order_1.remove_order_line('P002') -> {order_1.remove_order_line('P002')}")
    order_1.display_order()
    print("The mouse Product itself is untouched:")
    mouse.display_information()

    print("\nDiscard Order O002 - its OrderLine goes with it, the laptop does not:")
    del order_2
    laptop.display_information()


# ---------------------------------------------------------------- Section 6
def show_product_details(product: Product) -> None:
    # Accepts any Product. Never asks which subclass it was given.
    product.display_information()
    print(product.get_fulfilment_info())


def demo_lsp() -> None:
    heading("6. LISKOV SUBSTITUTION: any Product works where Product is expected")

    supplier = Supplier("S002", "Melody Music Supply", "orders@melodymusic.example")
    licences = Supplier("S003", "SoftKey Licensing", "licences@softkey.example")
    guitar = PhysicalProduct("P003", "Guitar", 450.00, 5, supplier, 3.5)
    editor = DigitalProduct("D002", "Photo Editor", 59.00, 50, licences, 850.0)

    print("show_product_details(guitar):")
    show_product_details(guitar)
    print("\nshow_product_details(editor):")
    show_product_details(editor)

    print("\nupdate_stock() keeps Product's meaning for both subclasses:")
    for product in (guitar, editor):
        print(f"  {product.get_name():<13} update_stock(8) -> {product.update_stock(8)}"
              f" (stock {product.get_stock()}) | update_stock(-1) -> "
              f"{product.update_stock(-1)} (stock {product.get_stock()})")


# ---------------------------------------------------------------- Section 7
def demo_polymorphism() -> None:
    heading("7. POLYMORPHISM: one loop over the Product collection")

    techworld = Supplier("S001", "TechWorld Distributors", "sales@techworld.example")
    licences = Supplier("S003", "SoftKey Licensing", "licences@softkey.example")
    inventory = Inventory("Main")
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, techworld, 2.0))
    inventory.add_product(DigitalProduct("D001", "Operating System", 139.99, 100, licences, 5200.0))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.50, 40, techworld, 0.1))
    inventory.add_product(DigitalProduct("D002", "Photo Editor", 59.00, 50, licences, 850.0))

    # One loop, no isinstance(): each object runs its own implementation.
    for product in inventory.products:
        product.display_information()
        print(f"    Fulfilment: {product.get_fulfilment_info()}")


if __name__ == "__main__":
    demo_association()
    demo_aggregation()
    demo_composition()
    demo_lsp()
    demo_polymorphism()
