from abc import ABC, abstractmethod

from supplier import Supplier


class Product(ABC):
    """Abstract base class for every product in the inventory.

    A product is always either physical or digital, so Product itself can
    never be instantiated. It holds the state and behaviour that all
    products share; subclasses extend it with their own attributes.

    Validation (Lab 9): Product owns the price and stock rules, so every
    subclass gets them automatically and no Product can exist in an
    invalid state.
      * price must be a number greater than zero
      * stock must be a whole number that is not negative

    Contract every subclass must keep (Liskov Substitution Principle):
      * update_stock(quantity) accepts any non-negative int and stores it;
        anything else raises ValueError and leaves the stock unchanged.
        No subclass may skip, loosen or tighten this rule.
      * get_fulfilment_info() always returns a str describing delivery.
      * display_information() prints the product and returns None.
    """

    def __init__(self, product_id: str, name: str, price: float,
                 stock: int, supplier: Supplier) -> None:
        Product.__validate_price(price)
        Product.__validate_stock(stock)
        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        # Association: a reference to a Supplier that was created elsewhere.
        # The Product does not create or own it.
        self.__supplier: Supplier = supplier

    # ---------- validation rules (one place for each rule) ----------

    @staticmethod
    def __validate_price(price: float) -> None:
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be greater than zero.")

    @staticmethod
    def __validate_stock(quantity: int) -> None:
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Stock quantity must be a whole number and cannot be negative.")

    # Read-only access to the private attributes
    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def update_stock(self, quantity: int) -> None:
        # Same rule as the constructor, so stock can never become invalid.
        Product.__validate_stock(quantity)
        self.__stock = quantity

    def display_information(self) -> None:
        print(f"ID: {self.__product_id} | Name: {self.__name} | "
              f"Price: ${self.__price:.2f} | Stock: {self.__stock} | "
              f"Supplier: {self.__supplier.get_name()}")

    def display_supplier_information(self) -> None:
        # Uses the association: asks the Supplier to describe itself.
        print(f"{self.__name} is supplied by:")
        self.__supplier.display_information()

    def to_dict(self) -> dict[str, str | float | int]:
        # Plain data form used by the file handling code when saving.
        # Only the supplier's ID is saved - the Supplier is saved separately.
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier_id": self.__supplier.get_supplier_id(),
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Return a message describing how this product reaches the customer."""
