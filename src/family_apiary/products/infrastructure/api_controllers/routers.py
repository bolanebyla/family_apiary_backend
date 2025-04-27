from fastapi import APIRouter

from family_apiary.products.infrastructure.api_controllers.v1.product_purchase_requests import (
    purchase_requests_router,
)

products_v1_router = APIRouter(prefix='/v1')

products_v1_router.include_router(
    purchase_requests_router,
    tags=['Заявки на покупку продукции'],
)


products_router = APIRouter(prefix='/products')

products_router.include_router(
    products_v1_router,
)
