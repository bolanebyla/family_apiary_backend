from dataclasses import dataclass, field
from datetime import datetime

from commons.value_objects import MoneyDecimal, PhoneNumber, PositiveInt


@dataclass
class NewPurchaseRequestNotificationProduct:
    name: str
    description: str
    price: float
    count: PositiveInt
    total_price: float


@dataclass
class NewPurchaseRequestNotification:
    phone_number: PhoneNumber
    name: str
    created_at: datetime
    total_price: float
    products: list[NewPurchaseRequestNotificationProduct] = field(
        default_factory=list,
    )
