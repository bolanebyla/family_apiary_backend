from dataclasses import dataclass, field

from commons.cqrs.base import CommandHandler
from commons.datetime_utils import now_tz
from commons.entities.base import create_entity_id
from commons.value_objects import MoneyDecimal, PhoneNumber, PositiveInt
from family_apiary.products.application.dto import (
    NewPurchaseRequestNotification,
    NewPurchaseRequestNotificationProduct,
)
from family_apiary.products.application.interfaces import (
    ProductPurchaseRequestNotificator,
)
from family_apiary.products.domain.entities import (
    PurchaseRequest,
    PurchaseRequestProduct,
)
from family_apiary.products.domain.repositories import PurchaseRequestRepo


@dataclass
class CreatePurchaseRequestCommandProduct:
    name: str
    description: str
    category: str
    price: MoneyDecimal
    count: PositiveInt


@dataclass
class CreatePurchaseRequestCommand:
    """
    Команда на создание заявки на покупку продукции
    """

    phone_number: PhoneNumber
    name: str
    products: list[CreatePurchaseRequestCommandProduct] = field(
        default_factory=list,
    )


class CreatePurchaseRequestHandler(
    CommandHandler[CreatePurchaseRequestCommand, None]
):
    """
    Создание заявку на покупку продукции
    """

    def __init__(
        self,
        purchase_request_repo: PurchaseRequestRepo,
        product_purchase_request_notificator: ProductPurchaseRequestNotificator,
    ):
        self._purchase_request_repo = purchase_request_repo
        self._product_purchase_request_notificator = (
            product_purchase_request_notificator
        )

    async def handle(self, command: CreatePurchaseRequestCommand) -> None:
        now = now_tz()

        purchase_request = PurchaseRequest(
            id=create_entity_id(),
            created_at=now,
            updated_at=now,
            name=command.name,
            phone_number=command.phone_number,
            products=[
                PurchaseRequestProduct(
                    id=create_entity_id(),
                    created_at=now,
                    updated_at=now,
                    name=command_product.name,
                    description=command_product.description,
                    price=command_product.price,
                    count=command_product.count,
                    category=command_product.category,
                )
                for command_product in command.products
            ],
        )

        await self._purchase_request_repo.add(purchase_request)

        notification = NewPurchaseRequestNotification(
            phone_number=purchase_request.phone_number,
            name=purchase_request.name,
            created_at=now,
            total_price=purchase_request.get_total_price(),
            products=[
                NewPurchaseRequestNotificationProduct(
                    name=purchase_request_product.name,
                    description=purchase_request_product.description,
                    price=purchase_request_product.price,
                    total_price=purchase_request_product.get_total_price(),
                    count=purchase_request_product.count,
                )
                for purchase_request_product in purchase_request.products
            ],
        )

        await self._product_purchase_request_notificator.send_new_request_notification(
            notification=notification,
        )
