from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """Strategy pattern: one interchangeable way of discounting an order total.

    Every strategy offers the same apply() method. Order only ever calls
    apply() and never checks which strategy it was given, so a new kind of
    discount is a new subclass here and Order does not change (Open/Closed
    Principle).
    """

    @abstractmethod
    def apply(self, total: float) -> float:
        """Return the total after this discount has been applied."""


class NoDiscount(DiscountStrategy):
    """Default strategy: the customer pays the full total."""

    def apply(self, total: float) -> float:
        return total

    def __str__(self) -> str:
        return "No discount"


class PercentageDiscount(DiscountStrategy):
    """Takes a percentage off any total, e.g. PercentageDiscount(10) = 10% off."""

    def __init__(self, percentage: float) -> None:
        # Validation: the strategy protects its own rule.
        if not 0 <= percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        self.__percentage: float = percentage

    def get_percentage(self) -> float:
        return self.__percentage

    def apply(self, total: float) -> float:
        return total - total * self.__percentage / 100

    def __str__(self) -> str:
        return f"{self.__percentage:g}% off"


class BulkDiscount(DiscountStrategy):
    """Takes a fixed amount off any total at or above a threshold.

    BulkDiscount(200, 20) takes $20 off any total of $200 or more.
    """

    def __init__(self, threshold: float, amount: float) -> None:
        if threshold < 0 or amount < 0:
            raise ValueError("Bulk discount threshold and amount cannot be negative.")
        self.__threshold: float = threshold
        self.__amount: float = amount

    def get_threshold(self) -> float:
        return self.__threshold

    def get_amount(self) -> float:
        return self.__amount

    def apply(self, total: float) -> float:
        # This if is the bulk rule itself, not a choice between discount types.
        if total >= self.__threshold:
            return max(total - self.__amount, 0.0)
        return total

    def __str__(self) -> str:
        return f"${self.__amount:g} off orders of ${self.__threshold:g} or more"


class StudentDiscount(PercentageDiscount):
    """Section 2.4: a fourth strategy, added without changing Order at all.

    A student discount is a fixed 5% off. It reuses PercentageDiscount's
    calculation, and keeps the student rate in one named place so the
    business can change it without touching any other class.
    """

    STUDENT_RATE: float = 5.0

    def __init__(self) -> None:
        super().__init__(StudentDiscount.STUDENT_RATE)

    def __str__(self) -> str:
        return f"Student discount ({StudentDiscount.STUDENT_RATE:g}% off)"
