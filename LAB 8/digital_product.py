from product import Product
from supplier import Supplier


class DigitalProduct(Product):
    """A product delivered by download (e.g. an operating system).

    Does not implement CanBeShipped, because nothing is physically shipped.

    Stock here means the number of licence keys available to sell, so
    update_stock() keeps exactly the meaning Product gives it (LSP). It is
    inherited unchanged rather than overridden to raise an error.
    """

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__download_size: float = download_size

    def get_download_size(self) -> float:
        return self.__download_size

    def display_information(self) -> None:
        # Parent prints the common details; the child adds its own.
        super().display_information()
        print(f"    Type: Digital | Download size: {self.__download_size:.2f} MB")

    def get_fulfilment_info(self) -> str:
        return f"{self.get_name()} is delivered digitally via a download link."

    def to_dict(self) -> dict[str, str | float | int]:
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data
