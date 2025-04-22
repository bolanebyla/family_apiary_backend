from fastapi import APIRouter

from family_apiary.products.application.use_cases.commands import (
    CreateProductPurchaseRequestCommand,
    CreateProductPurchaseRequestHandler,
)

product_requests_router = APIRouter(prefix='/product_requests')


@product_requests_router.post('/submit')
async def submit_product_requests():
    # TODO: использовать DI

    command = CreateProductPurchaseRequestCommand()

    handler = CreateProductPurchaseRequestHandler()
    await handler.handle(command)

    print('Ура!')
    return 'ok'
