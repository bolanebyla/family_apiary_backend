from fastapi import APIRouter

product_requests_router = APIRouter(prefix='/product_requests')


@product_requests_router.post('/submit')
async def submit_product_requests():
    print('Ура!')
    return 'ok'
