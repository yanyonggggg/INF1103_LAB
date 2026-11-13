from product import Product


class OrderLine:
    """One product and the quantity of it requested in an Order.

    Composition part: an OrderLine is created only by Order.add_order_line()
    and belongs to exactly one Order. It is never passed into an Order from
    outside and never moved to another Order.

    Association with Product: the OrderLine refers to a Product but does
    not own it. The same Product can be in an Inventory and in many orders.
    """

    def __init__(self, product: Product, quantity: int) -> None:
        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(f"  {self.__product.get_product_id()} {self.__product.get_name():<20} "
              f"x{self.__quantity:<3} @ ${self.__product.get_price():>8.2f} "
              f"= ${self.calculate_subtotal():>9.2f}")
