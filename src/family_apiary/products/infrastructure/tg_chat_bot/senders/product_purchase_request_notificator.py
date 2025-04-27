from typing import override

from aiogram import Bot

from family_apiary.products.application.dto import (
    NewPurchaseRequestNotification,
)
from family_apiary.products.application.interfaces import (
    ProductPurchaseRequestNotificator,
)


# TODO: добавить ограничение на длину сообщений (1-4096 символов)
class _NewRequestNotificationMessageText:
    """
    Текст для уведомления о новой заявке о покупке продукции
    """

    def __init__(
        self,
        notification: NewPurchaseRequestNotification,
    ):
        self._notification = notification

        self._message_text = self._create_message_text()

        if self._notification.products:
            self._message_text = (
                self._add_products_info_to_new_request_notification_text(
                    text=self._message_text,
                )
            )

    def _create_message_text(self) -> str:
        """
        Создаёт текст для уведомления о новой заявке о покупке продукции
        """
        text = (
            'Заявка на покупку продукции\n\n'
            f'Имя: {self._notification.name}\n'
            f'Телефон: {self._notification.phone_number}'
        )
        return text

    def _add_products_info_to_new_request_notification_text(
        self,
        text: str,
    ) -> str:
        """
        Добавляет в текст для уведомления о новой заявке о покупке продукции
        информацию о продукции
        """
        text += '\n\nКорзина:\n'
        for product in self._notification.products:
            text += (
                f'- {product.name}: {product.price} руб × {product.count} '
                f'= {product.total_price} руб\n'
            )

        text += f'\nИтого: {self._notification.total_price} руб'
        return text

    def to_string(self) -> str:
        return self._message_text

    def __str__(self) -> str:
        return self.to_string()


class ProductPurchaseRequestNotificatorImpl(ProductPurchaseRequestNotificator):
    def __init__(
        self,
        bot: Bot,
        notification_chat_id: str,
    ):
        self._bot = bot
        self._notification_chat_id = notification_chat_id

    @override
    async def send_new_request_notification(
        self,
        notification: NewPurchaseRequestNotification,
    ) -> None:
        notification_text = _NewRequestNotificationMessageText(
            notification=notification,
        )

        await self._bot.send_message(
            chat_id=self._notification_chat_id,
            text=notification_text.to_string(),
        )
