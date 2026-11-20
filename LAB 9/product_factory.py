from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from supplier import Supplier


class ProductFactory:
    """Factory pattern: the one place that decides which Product to build.

    The rest of the program asks for a product by its type name and gets
    back a Product. Only this class knows about PhysicalProduct and
    DigitalProduct, so client code depends on Product alone (low coupling)
    and uses it polymorphically.

    The factory creates products but does not store them (a dependency,
    not an association).

    Trade-off: adding a new product type still means editing create(), so
    the factory itself does not follow the Open/Closed Principle. That is
    accepted here because it is one small, obvious place to change, which is
    the simplest design for an application of this size.
    """

    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier,
               weight: float = 0.0, download_size: float = 0.0) -> Product:
        # weight is only used by physical products, download_size only by
        # digital ones. Both default to 0.0 when the source data (e.g. the
        # products CSV file) does not include them.
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, weight)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")
