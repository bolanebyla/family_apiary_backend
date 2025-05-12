from dishka import Provider, Scope, provide

from family_apiary.products.domain.repositories import PurchaseRequestRepo
from family_apiary.products.infrastructure.database.repositories.purchase_request_repo import (
    PurchaseRequestRepoImpl,
)


class DBRepositoriesProvider(Provider):
    scope = Scope.REQUEST

    purchase_request_repo = provide(
        PurchaseRequestRepoImpl,
        provides=PurchaseRequestRepo,
    )
