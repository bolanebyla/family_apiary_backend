from dishka import Provider, Scope, provide

from commons.mappers import Mapper, MapperConfig
from commons.mappers.mapper_impl import MapperImpl
from family_apiary.products.application.use_cases.commands import (
    CreatePurchaseRequestCommand,
    create_purchase_request_command_to_purchase_request_mapper_config,
)
from family_apiary.products.domain.entities import PurchaseRequest


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    def create_purchase_request_command_to_purchase_request_mapper(
        self,
    ) -> Mapper[
        MapperConfig[CreatePurchaseRequestCommand, PurchaseRequest],
        CreatePurchaseRequestCommand,
        PurchaseRequest,
    ]:
        return MapperImpl(
            mapper_config=create_purchase_request_command_to_purchase_request_mapper_config,
        )
