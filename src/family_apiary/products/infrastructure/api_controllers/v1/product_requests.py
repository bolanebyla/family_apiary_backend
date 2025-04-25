from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from commons.cqrs.base import CommandMediator
from family_apiary.products.application.use_cases.commands import (
    CreateProductPurchaseRequestCommand,
)

product_requests_router = APIRouter(prefix='/product_requests')


@product_requests_router.post('/submit')
@inject  # TODO: ? должен быть основной роутер
async def submit_product_requests(
    command_mediator: FromDishka[CommandMediator],
) -> None:
    # TODO: использовать DI
    command = CreateProductPurchaseRequestCommand()
    await command_mediator.send(command=command)
    return None
