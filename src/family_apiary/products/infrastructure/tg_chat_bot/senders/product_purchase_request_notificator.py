from typing import override

from aiogram import Bot

from family_apiary.products.application.dto import (
    NewProductPurchaseRequestNotification,
)
from family_apiary.products.application.interfaces import (
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
    async def send_new_request_notification(
        self,
        notification: NewProductPurchaseRequestNotification,
    ) -> None:
        notification_text = self._create_new_request_notification_text(
            notification=notification,
        )
        await self._bot.send_message(
            chat_id=self._notification_chat_id,
            text=notification_text,
        )

    def _create_new_request_notification_text(
        self, notification: NewProductPurchaseRequestNotification
    ) -> str:
        """
        Создаёт текст для уведомления о новой заявке о покупке продукции
        """
        text = (
            'Заявка на покупку продукции\n\n'
            f'Имя: {notification.name}\n'
            f'Телефон: {notification.phone_number}'
        )

        if notification.products:
            text = self._add_products_info_to_new_request_notification_text(
                text=text,
                notification=notification,
            )

        return text

    def _add_products_info_to_new_request_notification_text(
        self,
        text: str,
        notification: NewProductPurchaseRequestNotification,
    ) -> str:
        """
        Добавляет в текст для уведомления о новой заявке о покупке продукции
        информацию о продукции
        """
        text += '\n\nКорзина:\n'
        for product in notification.products:
            text += (
                f'- {product.name}: {product.price} руб × {product.count} '
                f'= {product.total_price} руб\n'
            )

        text += f'\nИтого: {notification.total_price} руб'
        return text
