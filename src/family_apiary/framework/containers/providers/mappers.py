from dishka import Provider, Scope, provide

from commons.mappers import Mapper, MapperConfig
from commons.mappers.pydantic_mapper import PydanticMapper
from family_apiary.products.application.dto import (
    NewPurchaseRequestNotification,
)
from family_apiary.products.application.use_cases.commands import (
    CreatePurchaseRequestCommand,
    create_purchase_request_command_to_purchase_request_mapper_config,
    purchase_request_to_new_purchase_request_notification_mapper_config,
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
        return PydanticMapper(
            mapper_config=create_purchase_request_command_to_purchase_request_mapper_config,
        )

    @provide
    def create_purchase_request_to_new_purchase_request_notification_mapper_config(
        self,
    ) -> Mapper[
        MapperConfig[PurchaseRequest, NewPurchaseRequestNotification],
        PurchaseRequest,
        NewPurchaseRequestNotification,
    ]:
        return PydanticMapper(
            mapper_config=purchase_request_to_new_purchase_request_notification_mapper_config,
        )
