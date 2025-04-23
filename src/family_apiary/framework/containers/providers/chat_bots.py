from typing import AsyncIterable, Iterable

from aiogram import Bot
from dishka import Provider, Scope, provide

from family_apiary.products.application.use_cases.interfaces import (
    ProductPurchaseRequestNotificator,
)
from family_apiary.products.infrastructure.tg_chat_bot import (
    ProductPurchaseRequestNotificatorImpl,
    TgChatBotSettings,
)


class TgChatBotProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def create_tg_chat_bot(
        self,
        tg_chat_bot_settings: TgChatBotSettings,
    ) -> AsyncIterable[Bot]:
        tg_bot = Bot(
            token=tg_chat_bot_settings.TOKEN,
        )
        async with tg_bot:
            yield tg_bot

    @provide
    def create_product_purchase_request_notificator(
        self,
        tg_bot: Bot,
        tg_chat_bot_settings: TgChatBotSettings,
    ) -> ProductPurchaseRequestNotificator:
        return ProductPurchaseRequestNotificatorImpl(
            bot=tg_bot,
            notification_chat_id=tg_chat_bot_settings.PRODUCT_PURCHASE_REQUEST_NOTIFICATION_CHAT_ID,
        )
