from __future__ import annotations

from product import Product


class Inventory:
    """Manages a collection of Product objects.

    Aggregation with Product: the Inventory is a whole made of Product
    parts, but it does not create them and does not control their
    lifecycle. Products are created elsewhere, added here, and can be
    removed or transferred to another Inventory without being destroyed.

    The collection is typed with the base class Product, so it can hold a
    PhysicalProduct, a DigitalProduct, or any Product subclass added later.
    Inventory never checks which subclass it is dealing with.
    """

    def __init__(self, name: str = "Main") -> None:
        self.__name: str = name
        self.__products: list[Product] = []

    def get_name(self) -> str:
        return self.__name

    @property
    def products(self) -> list[Product]:
        # Copy of the list so callers cannot alter the collection directly.
        return list(self.__products)

    def get_products(self) -> list[Product]:
        return self.products

    def add_product(self, product: Product) -> bool:
        # Adds an existing Product. Returns False if the ID is already used.
        if self.find_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def remove_product(self, product_id: str) -> Product | None:
        # Removes the reference only. The Product object itself is handed
        # back to the caller untouched, so it can be used or added elsewhere.
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        # Returns the matching Product, or None if not found.
        for product in self.__products:
            if product.get_product_id().lower() == product_id.lower():
                return product
        return None

    def transfer_product(self, product_id: str, target: Inventory) -> bool:
        # Moves the same Product object to another Inventory.
        product = self.find_product(product_id)
        if product is None or target.find_product(product_id) is not None:
            return False
        self.remove_product(product_id)
        target.add_product(product)
        return True

    def clear(self) -> None:
        # Empties the inventory. The products still exist wherever else
        # they are referenced - only this collection forgets them.
        self.__products.clear()

    def display_all_products(self) -> None:
        print(f"\nInventory: {self.__name}")
        if not self.__products:
            print("No products available.")
            return
        for product in self.__products:
            # Polymorphism: each product displays itself its own way.
            product.display_information()
