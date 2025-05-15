from dataclasses import dataclass
from typing import Any, Iterable, Type

from dataclass_mapper import create_mapper, map_to

from commons.mappers.mapper import C, Mapper, MapperConfig, R, T


class MapperImpl(Mapper[C, T, R]):
    def __init__(self, mapper_config: MapperConfig[T, R]):
        self.mapper_config = mapper_config

        for nested_mapper_config in mapper_config.nested_mappers:
            self._init_mapper(mapper_config=nested_mapper_config)

        self._init_mapper(mapper_config=mapper_config)

    @staticmethod
    def _init_mapper(mapper_config: MapperConfig[Type, Type]) -> None:
        fields_mapping = (
            mapper_config.field_mappings | mapper_config.computed_fields
        )
        create_mapper(
            SourceCls=mapper_config.source_type,
            TargetCls=mapper_config.target_type,
            mapping=fields_mapping,
        )

    def map(
        self,
        source: T,
        extra: dict[str, Any] | None = None,
    ) -> R:
        return map_to(
            obj=source,
            target=self.mapper_config.target_type,
            extra=extra,
        )

    def map_many(
        self,
        sources: Iterable[T],
        extra: dict[str, Any] | None = None,
    ) -> list[R]:
        return [self.map(source, extra) for source in sources]


if __name__ == '__main__':

    @dataclass
    class Person:
        id: int
        name: str

    @dataclass
    class Contact:
        id: int
        title: str
        slug: str

    class ContactMapperConfig(MapperConfig[Person, Contact]):
        source_type = Person
        target_type = Contact

        field_mappings = {'title': 'name'}
        computed_fields = {'slug': lambda source: f'{source.id}_{source.name}'}

    contact_mapper_config = ContactMapperConfig()
    contact_mapper = MapperImpl(mapper_config=contact_mapper_config)

    person = Person(id=1, name='test_name')

    contact = contact_mapper.map(person)
    print(contact)
