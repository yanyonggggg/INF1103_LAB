class Supplier:
    """A company that supplies products.

    Association with Product: a Supplier and a Product only *know about*
    each other. Neither is part of the other, and either can exist without
    the other. The Product keeps a reference to its Supplier; the Supplier
    does not keep a list of its products (loose coupling - it does not need
    one for anything this system does).
    """

    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        self.__supplier_id: str = supplier_id
        self.__name: str = name
        self.__contact_email: str = contact_email

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self.__supplier_id} | Name: {self.__name} | "
              f"Email: {self.__contact_email}")

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.__supplier_id,
            "name": self.__name,
            "email": self.__contact_email,
        }
