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


create_purchase_request_command_product_mapper_config = MapperConfig(
    source_type=CreatePurchaseRequestCommandProduct,
    target_type=PurchaseRequestProduct,
    computed_fields={
        'id': lambda value: create_entity_id(),
    },
)

create_purchase_request_command_to_purchase_request_mapper_config = (
    MapperConfig(
        source_type=CreatePurchaseRequestCommand,
        target_type=PurchaseRequest,
        computed_fields={
            'id': lambda source: create_entity_id(),
        },
        nested_mapper_configs=[
            create_purchase_request_command_product_mapper_config,
        ],
    )
)

purchase_request_product_to_new_purchase_request_notification_product_mapper_config = MapperConfig(
    source_type=PurchaseRequestProduct,
    target_type=NewPurchaseRequestNotificationProduct,
    computed_fields={
        'total_price': lambda source: source.get_total_price(),
    },
)

purchase_request_to_new_purchase_request_notification_mapper_config = MapperConfig(
    source_type=PurchaseRequest,
    target_type=NewPurchaseRequestNotification,
    computed_fields={
        'total_price': lambda source: source.get_total_price(),
    },
    nested_mapper_configs=[
        purchase_request_product_to_new_purchase_request_notification_product_mapper_config,
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
        purchase_request_mapper: Mapper[
            MapperConfig[CreatePurchaseRequestCommand, PurchaseRequest],
            CreatePurchaseRequestCommand,
            PurchaseRequest,
        ],
        new_purchase_request_notification_mapper: Mapper[
            MapperConfig[PurchaseRequest, NewPurchaseRequestNotification],
            PurchaseRequest,
            NewPurchaseRequestNotification,
        ],
        product_purchase_request_notificator: ProductPurchaseRequestNotificator,
    ):
        self._purchase_request_repo = purchase_request_repo
        self._purchase_request_mapper = purchase_request_mapper
        self._new_purchase_request_notification_mapper = (
            new_purchase_request_notification_mapper
        )
        self._product_purchase_request_notificator = (
            product_purchase_request_notificator
        )

    async def handle(self, command: CreatePurchaseRequestCommand) -> None:
        now = now_tz()

        purchase_request = self._purchase_request_mapper.map(
            source=command,
            extra={
                'created_at': now,
                'updated_at': now,
            },
        )

        await self._purchase_request_repo.add(purchase_request)

        notification = self._new_purchase_request_notification_mapper.map(
            purchase_request,
            extra={
                'created_at': now,
            },
        )

        await self._product_purchase_request_notificator.send_new_request_notification(
            notification=notification,
        )
