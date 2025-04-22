from abc import abstractmethod
from typing import Protocol


class ProductPurchaseRequestNotificator(Protocol):
    @abstractmethod
    async def send_new_request_notification(self) -> None:
        """
        Отправляет уведомление о новой заявке на покупку продукции
        """
