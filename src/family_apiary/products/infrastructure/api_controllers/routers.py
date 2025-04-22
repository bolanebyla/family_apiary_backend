from fastapi import APIRouter

from family_apiary.products.infrastructure.api_controllers.v1.product_requests import \
    product_requests_router

products_v1_router = APIRouter(prefix='/v1')

products_v1_router.include_router(
    product_requests_router,
    tags=['Заявки на покупку продукции'],
)
