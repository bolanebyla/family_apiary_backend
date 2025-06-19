from dataclasses import dataclass, field

from commons.cqrs.base import CommandHandler
from commons.datetime_utils import now_tz
from commons.entities.base import create_entity_id
from commons.mappers import Mapper, MapperConfig
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
    price: float
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


product_mapper_config = MapperConfig(
    source_type=CreatePurchaseRequestCommandProduct,
    target_type=PurchaseRequestProduct,
    computed_fields={
        'id': lambda value: create_entity_id(),
    },
)

purchase_request_mapper_config = MapperConfig(
    source_type=CreatePurchaseRequestCommand,
    target_type=PurchaseRequest,
    computed_fields={
        'id': lambda source: create_entity_id(),
    },
    nested_mapper_configs=[
        product_mapper_config,
    ],
)

notification_product_mapper_config = MapperConfig(
    source_type=PurchaseRequestProduct,
    target_type=NewPurchaseRequestNotificationProduct,
    computed_fields={
        'total_price': lambda source: source.get_total_price(),
    },
)

notification_mapper_config = MapperConfig(
    source_type=PurchaseRequest,
    target_type=NewPurchaseRequestNotification,
    computed_fields={
        'total_price': lambda source: source.get_total_price(),
    },
    nested_mapper_configs=[
        notification_product_mapper_config,
    ],
)


class CreatePurchaseRequestHandler(
    CommandHandler[CreatePurchaseRequestCommand, None]
):
    """
    Создание заявки на покупку продукции
    """

    def __init__(
        self,
        purchase_request_repo: PurchaseRequestRepo,
        mapper: Mapper,
        product_purchase_request_notificator: ProductPurchaseRequestNotificator,
    ):
        self._purchase_request_repo = purchase_request_repo
        self._mapper = mapper
        self._product_purchase_request_notificator = (
            product_purchase_request_notificator
        )

    async def handle(self, command: CreatePurchaseRequestCommand) -> None:
        now = now_tz()

        purchase_request = self._mapper.map(
            source=command,
            mapper_config=purchase_request_mapper_config,
            extra={
                'created_at': now,
                'updated_at': now,
            },
        )

        await self._purchase_request_repo.add(purchase_request)

        notification = self._mapper.map(
            purchase_request,
            mapper_config=notification_mapper_config,
            extra={
                'created_at': now,
            },
        )

        await self._product_purchase_request_notificator.send_new_request_notification(
            notification=notification,
        )
