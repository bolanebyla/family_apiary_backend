from dataclasses import dataclass

from commons.entities.base import BaseEntity
from commons.value_objects import MoneyDecimal, PositiveInt


@dataclass
class PurchaseRequestProduct(BaseEntity):
    """
    Продукт из заявки на покупку
    """

    name: str
    description: str
    category: str
    price: MoneyDecimal
    count: PositiveInt

    def get_total_price(self) -> MoneyDecimal:
        return self.price * self.count
