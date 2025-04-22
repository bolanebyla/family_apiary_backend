from dataclasses import dataclass

from commons.cqrs.base import CommandHandler


@dataclass
class CreateProductPurchaseRequestCommand:
    pass


class CreateProductPurchaseRequestHandler(
    CommandHandler[CreateProductPurchaseRequestCommand, None]
):
    async def handle(
        self, command: CreateProductPurchaseRequestCommand
    ) -> None:
        # TODO: create and save

        # TODO: send notification
        print('Запрос получен')
