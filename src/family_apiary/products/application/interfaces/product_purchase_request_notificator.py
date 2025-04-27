from abc import abstractmethod
from typing import Protocol

from family_apiary.products.application.dto import (
    NewPurchaseRequestNotification,
)


class ProductPurchaseRequestNotificator(Protocol):
    """
    Отправка уведомлений о новой продукции
    """

    @abstractmethod
    async def send_new_request_notification(
        self,
        notification: NewPurchaseRequestNotification,
    ) -> None:
        """
        Отправляет уведомление о новой заявке на покупку продукции
        """
        ...
