from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from commons.cqrs.base import CommandMediator
from commons.value_objects import PhoneNumber
from family_apiary.products.application.use_cases.commands import (
    CreateProductPurchaseRequestCommand,
    CreateProductPurchaseRequestCommandProduct,
)
from family_apiary.products.infrastructure.api_controllers.v1.schemas import (
    CreateProductPurchaseRequest,
)

product_purchase_requests_router = APIRouter(
    prefix='/product_purchase_requests',
    route_class=DishkaRoute,
)


@product_purchase_requests_router.post('/submit')
async def submit_product_purchase_request(
    create_product_purchase_request: CreateProductPurchaseRequest,
    command_mediator: FromDishka[CommandMediator],
) -> None:
    command = CreateProductPurchaseRequestCommand(
        phone_number=PhoneNumber(create_product_purchase_request.phone_number),
        name=create_product_purchase_request.name,
        products=[
            CreateProductPurchaseRequestCommandProduct(
                id=req_product.id,
                name=req_product.name,
                description=req_product.description,
                price=req_product.price,
                category=req_product.category,
            )
            for req_product in create_product_purchase_request.products
        ],
    )
    await command_mediator.send(command=command)
    return None
