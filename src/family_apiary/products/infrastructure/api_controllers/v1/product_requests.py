from aiogram import Bot
from fastapi import APIRouter

from family_apiary.products.application.use_cases.commands import (
    CreateProductPurchaseRequestCommand,
    CreateProductPurchaseRequestHandler,
)
from family_apiary.products.infrastructure.tg_chat_bot import (
    ProductPurchaseRequestNotificatorImpl,
    TgChatBotSettings,
)

product_requests_router = APIRouter(prefix='/product_requests')


@product_requests_router.post('/submit')
async def submit_product_requests():
    # TODO: использовать DI
    settings = TgChatBotSettings()
    bot = Bot(token=settings.TOKEN)
    notificator = ProductPurchaseRequestNotificatorImpl(
        bot=bot,
        notification_chat_id=settings.PRODUCT_PURCHASE_REQUEST_NOTIFICATION_CHAT_ID,
    )

    command = CreateProductPurchaseRequestCommand()

    handler = CreateProductPurchaseRequestHandler(
        product_purchase_request_notificator=notificator,
    )
    await handler.handle(command)
    return 'ok'
