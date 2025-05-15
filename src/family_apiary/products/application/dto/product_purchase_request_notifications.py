from dataclasses import dataclass, field
from datetime import datetime

from commons.value_objects import MoneyDecimal, PhoneNumber, PositiveInt


@dataclass
class NewPurchaseRequestNotificationProduct:
    name: str
    description: str
    price: MoneyDecimal
    count: PositiveInt
    total_price: MoneyDecimal


@dataclass
class NewPurchaseRequestNotification:
    phone_number: PhoneNumber
    name: str
    created_at: datetime
    total_price: MoneyDecimal
    products: list[NewPurchaseRequestNotificationProduct] = field(
        default_factory=list,
    )
