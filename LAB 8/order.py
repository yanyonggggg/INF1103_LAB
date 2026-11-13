from order_line import OrderLine
from product import Product


class Order:
    """A customer order made up of OrderLine objects.

    Composition with OrderLine: the Order creates its own OrderLine objects
    inside add_order_line() and is the only thing that keeps them. When an
    order line is removed, or the Order itself is discarded, its lines go
    with it. OrderLines are never accepted from outside or transferred.
    """

    def __init__(self, order_id: str) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []

    def get_order_id(self) -> str:
        return self.__order_id

    def get_order_lines(self) -> tuple[OrderLine, ...]:
        # Read-only view: callers can look at the lines but cannot add,
        # remove or move them. Only Order changes its own collection.
        return tuple(self.__order_lines)

    def add_order_line(self, product: Product, quantity: int) -> None:
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")
        # The Order creates the part itself - this is what makes it composition.
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id().lower() == product_id.lower():
                # The line is discarded with nothing else referring to it.
                # The Product it pointed to is not affected.
                self.__order_lines.remove(order_line)
                return True
        return False

    def calculate_total(self) -> float:
        # The Order asks each of its lines for its subtotal.
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def display_order(self) -> None:
        print(f"\nOrder {self.__order_id}")
        if not self.__order_lines:
            print("  (no order lines)")
        for order_line in self.__order_lines:
            order_line.display_information()
        print(f"  {'TOTAL':<44} ${self.calculate_total():>9.2f}")
