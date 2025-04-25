from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from commons.cqrs.base import CommandMediator
from family_apiary.products.application.use_cases.commands import (
    CreateProductPurchaseRequestCommand,
)

product_purchase_requests_router = APIRouter(
    prefix='/product_purchase_requests',
    route_class=DishkaRoute,
)


@product_purchase_requests_router.post('/submit')
async def submit_product_purchase_request(
    command_mediator: FromDishka[CommandMediator],
) -> None:
    # TODO: использовать DI
    command = CreateProductPurchaseRequestCommand()
    await command_mediator.send(command=command)
    return None
