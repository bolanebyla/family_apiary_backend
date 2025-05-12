from family_apiary.products.domain.entities import PurchaseRequest
from family_apiary.products.domain.repositories import PurchaseRequestRepo


class PurchaseRequestRepoImpl(PurchaseRequestRepo):
    async def add(self, purchase_request: PurchaseRequest) -> None:
        # TODO: реализовать логику
        pass
