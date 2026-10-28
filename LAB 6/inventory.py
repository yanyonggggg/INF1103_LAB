class Inventory:
    """Manages a collection of Product objects."""

    def __init__(self):
        self.__products = []

    def add_product(self, product):
        # Returns False if a product with the same ID already exists.
        if self.search_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def search_product(self, product_id):
        # Returns the matching Product, or None if not found.
        for product in self.__products:
            if product.get_product_id().lower() == product_id.lower():
                return product
        return None

    def display_all(self):
        print("\nCurrent Inventory")
        if not self.__products:
            print("No products available.")
            return
        for product in self.__products:
            product.display_information()

    def get_products(self):
        # Copy of the list so callers cannot alter the collection directly.
        return list(self.__products)
