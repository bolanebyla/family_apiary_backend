from dishka import Provider, Scope, provide

from commons.mappers import Mapper
from commons.mappers.mapper_impl import MapperImpl


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    def create_mapper(
        self,
    ) -> Mapper:
        return MapperImpl()
