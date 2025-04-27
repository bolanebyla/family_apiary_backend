from dataclasses import dataclass, field
from decimal import Decimal

from commons.cqrs.base import CommandHandler
from commons.datetime_utils import now_tz
from commons.entities.base import EntityId
from commons.value_objects import PhoneNumber
from family_apiary.products.application.dto import (
    NewPurchaseRequestNotification,
    NewPurchaseRequestNotificationProduct,
)
from family_apiary.products.application.interfaces import (
    ProductPurchaseRequestNotificator,
)


@dataclass
class CreatePurchaseRequestCommandProduct:
    id: EntityId
    name: str
    description: str
    category: str
    price: Decimal  # TODO: positive Decimal
    count: int  # TODO: positive int


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
        product_purchase_request_notificator: ProductPurchaseRequestNotificator,
    ):
        self._product_purchase_request_notificator = (
            product_purchase_request_notificator
        )

    async def handle(self, command: CreatePurchaseRequestCommand) -> None:
        # TODO: create and save

        now = now_tz()

        notification = NewPurchaseRequestNotification(
            phone_number=command.phone_number,
            name=command.name,
            created_at=now,
            total_price=Decimal(
                1234
            ),  # TODO: рассчитывать итоговую стоимость в сущности
            products=[
                NewPurchaseRequestNotificationProduct(
                    name=command_product.name,
                    description=command_product.description,
                    price=command_product.price,
                    total_price=command_product.price
                    * command_product.count,  # TODO: вынести в сущность
                    count=command_product.count,
                )
                for command_product in command.products
            ],
        )

        await self._product_purchase_request_notificator.send_new_request_notification(
            notification=notification,
        )
