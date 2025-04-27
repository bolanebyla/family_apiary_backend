from dishka import Provider, Scope, provide

from family_apiary.products.application.use_cases.commands import (
    CreatePurchaseRequestHandler,
)


class CommandHandlersProvider(Provider):
    scope = Scope.REQUEST

    create_product_purchase_request_handler = provide(
        CreatePurchaseRequestHandler
    )
