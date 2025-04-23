from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from family_apiary.products.application.use_cases.commands import (
    CreateProductPurchaseRequestCommand,
    CreateProductPurchaseRequestHandler,
)
from family_apiary.products.application.use_cases.interfaces import (
    ProductPurchaseRequestNotificator,
)

product_requests_router = APIRouter(prefix='/product_requests')


@product_requests_router.post('/submit')
@inject  # TODO: ? должен быть основной роутер
async def submit_product_requests(
    notificator: FromDishka[ProductPurchaseRequestNotificator],
):
    # TODO: использовать DI
    command = CreateProductPurchaseRequestCommand()

    handler = CreateProductPurchaseRequestHandler(
        product_purchase_request_notificator=notificator,
    )
    await handler.handle(command)
    return 'ok'
