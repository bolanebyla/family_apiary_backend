from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from commons.cqrs.base import CommandMediator
from commons.value_objects import PhoneNumber
from family_apiary.products.application.use_cases.commands import (
    CreatePurchaseRequestCommand,
    CreatePurchaseRequestCommandProduct,
)
from family_apiary.products.infrastructure.api_controllers.v1.schemas import (
    CreatePurchaseRequest,
)

purchase_requests_router = APIRouter(
    prefix='/purchase_requests',
    route_class=DishkaRoute,
)


@purchase_requests_router.post('/submit')
async def submit_purchase_request(
    create_purchase_request: CreatePurchaseRequest,
    command_mediator: FromDishka[CommandMediator],
) -> None:
    command = CreatePurchaseRequestCommand(
        phone_number=PhoneNumber(create_purchase_request.phone_number),
        name=create_purchase_request.name,
        products=[
            CreatePurchaseRequestCommandProduct(
                id=req_product.id,
                name=req_product.name,
                description=req_product.description,
                price=req_product.price,
                category=req_product.category,
                count=req_product.count,
            )
            for req_product in create_purchase_request.products
        ],
    )
    await command_mediator.send(command=command)
    return None
