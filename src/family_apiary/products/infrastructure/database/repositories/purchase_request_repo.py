from commons.db.sqlalchemy import BaseRepository
from family_apiary.products.domain.entities import PurchaseRequest
from family_apiary.products.domain.repositories import PurchaseRequestRepo


class PurchaseRequestRepoImpl(BaseRepository, PurchaseRequestRepo):
    async def add(self, purchase_request: PurchaseRequest) -> None:
        self.session.add(purchase_request)
        await self.session.flush()
