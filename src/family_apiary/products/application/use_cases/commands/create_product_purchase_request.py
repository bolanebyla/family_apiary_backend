from dataclasses import dataclass

from commons.cqrs.base import CommandHandler


@dataclass
class CreateProductPurchaseRequestCommand:
    """
    Команда на создание заявку на покупку продукции
    """

    pass


class CreateProductPurchaseRequestHandler(
    CommandHandler[CreateProductPurchaseRequestCommand, None]
):
    """
    Создание заявку на покупку продукции
    """

    async def handle(
        self, command: CreateProductPurchaseRequestCommand
    ) -> None:
        # TODO: create and save

        # TODO: send notification
        print('Запрос получен')
