from abc import abstractmethod
from typing import Protocol

from family_apiary.products.domain.entities import PurchaseRequest


class PurchaseRequestRepo(Protocol):
    @abstractmethod
    async def add(self, purchase_request: PurchaseRequest) -> None: ...
