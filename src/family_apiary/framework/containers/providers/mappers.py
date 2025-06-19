from dishka import Provider, Scope, provide

from commons.mappers import Mapper
from commons.mappers.pydantic_mapper import PydanticMapper


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    def create_mapper(
        self,
    ) -> Mapper:
        return PydanticMapper()
