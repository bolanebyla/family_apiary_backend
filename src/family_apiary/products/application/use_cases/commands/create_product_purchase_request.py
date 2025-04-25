from dataclasses import dataclass

from commons.cqrs.base import CommandHandler
from family_apiary.products.application.use_cases.interfaces import (
    ProductPurchaseRequestNotificator,
)


@dataclass
class CreateProductPurchaseRequestCommand:
    """
    Команда на создание заявки на покупку продукции
    """

    pass


class CreateProductPurchaseRequestHandler(
    CommandHandler[CreateProductPurchaseRequestCommand, None]
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

    async def handle(
        self, command: CreateProductPurchaseRequestCommand
    ) -> None:
        # TODO: create and save

        # TODO: send notification
        print('Запрос получен')
        await self._product_purchase_request_notificator.send_new_request_notification()
