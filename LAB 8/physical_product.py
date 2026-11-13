from product import Product
from can_be_shipped import CanBeShipped
from supplier import Supplier


class PhysicalProduct(Product, CanBeShipped):
    """A product that is stored and shipped (e.g. a guitar).

    Inherits from one class (Product) and implements one interface
    (CanBeShipped).
    """

    BASE_SHIPPING_FEE: float = 5.00   # flat fee per shipment
    RATE_PER_KG: float = 2.50         # extra cost for each kilogram

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__weight: float = weight

    def get_weight(self) -> float:
        return self.__weight

    def display_information(self) -> None:
        # Parent prints the common details; the child adds its own.
        super().display_information()
        print(f"    Type: Physical | Weight: {self.__weight:.2f} kg | "
              f"Shipping: ${self.calculate_shipping_cost():.2f}")

    def get_fulfilment_info(self) -> str:
        return f"{self.get_name()} requires physical shipping to the customer."

    def calculate_shipping_cost(self) -> float:
        return self.BASE_SHIPPING_FEE + self.__weight * self.RATE_PER_KG

    def to_dict(self) -> dict[str, str | float | int]:
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data
