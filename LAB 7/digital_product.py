from product import Product


class DigitalProduct(Product):
    """A product delivered by download (e.g. an operating system).

    Does not implement CanBeShipped, because nothing is physically shipped.
    """

    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        self.__download_size = download_size

    def get_download_size(self):
        return self.__download_size

    def display_information(self):
        # Parent prints the common details; the child adds its own.
        super().display_information()
        print(f"    Type: Digital | Download size: {self.__download_size:.2f} MB")

    def get_fulfilment_info(self):
        return f"{self.get_name()} is delivered digitally via a download link."

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data
