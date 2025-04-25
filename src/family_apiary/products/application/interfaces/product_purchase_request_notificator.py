from abc import abstractmethod
from typing import Protocol

from family_apiary.products.application.dto import (
    NewProductPurchaseRequestNotification,
)


class ProductPurchaseRequestNotificator(Protocol):
    """
    Отправка уведомлений о новой продукции
    """

    @abstractmethod
    async def send_new_request_notification(
        self,
        notification: NewProductPurchaseRequestNotification,
    ) -> None:
        """
        Отправляет уведомление о новой заявке на покупку продукции
        """
        ...
