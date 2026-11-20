from discount_strategy import DiscountStrategy, NoDiscount
from order_line import OrderLine
from product import Product


class Order:
    """A customer order made up of OrderLine objects.

    Composition with OrderLine: the Order creates its own OrderLine objects
    inside add_order_line() and is the only thing that keeps them. When an
    order line is removed, or the Order itself is discarded, its lines go
    with it. OrderLines are never accepted from outside or transferred.

    Association with DiscountStrategy (Strategy pattern): the Order *uses*
    a discount strategy that is created outside it and passed in. It does
    not create or own the strategy, the same strategy object can be shared
    by many orders, and it can be swapped at any time with set_discount().
    Order contains no if/elif about discount types - it only calls apply().
    """

    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []
        # No strategy given -> the customer pays full price.
        self.__discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def get_order_id(self) -> str:
        return self.__order_id

    def get_order_lines(self) -> tuple[OrderLine, ...]:
        # Read-only view: callers can look at the lines but cannot add,
        # remove or move them. Only Order changes its own collection.
        return tuple(self.__order_lines)

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        # Swap the behaviour at run time. Order does not care which one it is.
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        # The Order creates the part itself - this is what makes it composition.
        # OrderLine validates its own quantity and raises ValueError if it is
        # invalid, so an invalid line is never appended.
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

    def calculate_subtotal(self) -> float:
        # The Order asks each of its lines for its subtotal.
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def calculate_total(self) -> float:
        # The Order adds up its lines; the strategy decides the discount.
        return self.__discount.apply(self.calculate_subtotal())

    def display_order(self) -> None:
        print(f"\nOrder {self.__order_id}")
        if not self.__order_lines:
            print("  (no order lines)")
        for order_line in self.__order_lines:
            order_line.display_information()
        subtotal = self.calculate_subtotal()
        total = self.calculate_total()
        print(f"  {'Subtotal':<44} ${subtotal:>9.2f}")
        print(f"  {'Discount: ' + str(self.__discount):<44} -${subtotal - total:>8.2f}")
        print(f"  {'TOTAL':<44} ${total:>9.2f}")
