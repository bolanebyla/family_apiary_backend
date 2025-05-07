from dataclasses import dataclass, field

from commons.entities.base import BaseEntity
from commons.value_objects import MoneyDecimal, PhoneNumber

from .purchase_request_product import (
    PurchaseRequestProduct,
)


@dataclass
class PurchaseRequest(BaseEntity):
    """
    Заявка на покупку продукции
    """

    phone_number: PhoneNumber
    name: str
    products: list[PurchaseRequestProduct] = field(
        default_factory=list,
    )

    def get_total_price(self) -> MoneyDecimal:
        total_price = MoneyDecimal.zero()
        for product in self.products:
            total_price += product.get_total_price()
        return total_price
