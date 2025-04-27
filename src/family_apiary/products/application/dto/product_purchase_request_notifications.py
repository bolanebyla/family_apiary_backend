from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from commons.value_objects import PhoneNumber


@dataclass
class NewPurchaseRequestNotificationProduct:
    name: str
    description: str
    price: Decimal
    count: int
    total_price: Decimal


@dataclass
class NewPurchaseRequestNotification:
    phone_number: PhoneNumber
    name: str
    created_at: datetime
    total_price: Decimal
    products: list[NewPurchaseRequestNotificationProduct] = field(
        default_factory=list,
    )
