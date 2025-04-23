from typing import override

from aiogram import Bot

from family_apiary.products.application.use_cases.interfaces import (
    ProductPurchaseRequestNotificator,
)


class ProductPurchaseRequestNotificatorImpl(ProductPurchaseRequestNotificator):
    def __init__(
        self,
        bot: Bot,
        notification_chat_id: str,
    ):
        self._bot = bot
        self._notification_chat_id = notification_chat_id

    @override
    async def send_new_request_notification(self) -> None:
        await self._bot.send_message(
            chat_id=self._notification_chat_id,
            text='Hello, world!',
        )
