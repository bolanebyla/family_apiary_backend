from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from inspect import isclass
from typing import Any, Callable, Iterable, Type, cast

from dataclass_mapper import create_mapper, from_extra, map_to
from dataclass_mapper.implementations.sqlalchemy import InstrumentedAttribute
from dataclass_mapper.special_field_mappings import (
    AssumeNotNone,
    FromExtra,
    Ignore,
    Spezial,
    UpdateOnlyIfSet,
)
from pydantic import BaseModel

from commons.mappers.mapper import (
    C,
    ComputedField,
    Mapper,
    MapperConfig,
    R,
    T,
)

ExpectedMapping = dict[
    str | InstrumentedAttribute,
    str
    | Callable[[], Any]
    | Callable[[Any], Any]
    | Ignore
    | AssumeNotNone
    | FromExtra
    | UpdateOnlyIfSet
    | Spezial
    | InstrumentedAttribute,
]

MAPPER_ALREADY_EXISTS_ERROR_MESSAGE = 'There already exists a mapping'


class MapperImpl(Mapper[C, T, R]):
    def __init__(self, mapper_config: MapperConfig[T, R]):
        self.mapper_config = mapper_config

        self._init_mapper(mapper_config=mapper_config)

    def _init_mapper(
        self,
        mapper_config: MapperConfig[Type, Type],
    ) -> None:
        try:
            self._init_nested_mapper_configs(
                nested_mapper_configs=mapper_config.nested_mapper_configs,
            )

            fields_mapping = self._create_fields_mapping(mapper_config)
            # Приводим к ожидаемому типу,
            # так как мы знаем, что наши типы совместимы
            expected_mapping = cast(ExpectedMapping, fields_mapping)

            create_mapper(
                SourceCls=mapper_config.source_type,
                TargetCls=mapper_config.target_type,
                mapping=expected_mapping,
            )
        except AttributeError as e:
            if e.args and MAPPER_ALREADY_EXISTS_ERROR_MESSAGE in e.args[0]:
                pass
            else:
                raise

    def _init_nested_mapper_configs(
        self, nested_mapper_configs: list[MapperConfig[Any, Any]]
    ) -> None:
        for nested_mapper_config in nested_mapper_configs:
            self._init_mapper(mapper_config=nested_mapper_config)

    def _create_fields_mapping(
        self,
        mapper_config: MapperConfig[Type, Type],
    ) -> dict[str, str | ComputedField | FromExtra]:
        fields_mapping: dict[str, str | ComputedField] = (
            mapper_config.field_mappings | mapper_config.computed_fields
        )

        extra_field_names = self._get_extra_field_names(
            mapper_config=mapper_config,
            fields_mapping=fields_mapping,
        )

        extra_fields_mapping = self._create_extra_fields_mapping(
            extra_field_names=extra_field_names,
        )
        return fields_mapping | extra_fields_mapping

    def _get_extra_field_names(
        self,
        mapper_config: MapperConfig[Type, Type],
        fields_mapping: dict[str, str | ComputedField],
    ) -> list[str]:
        source_type_fields = self._get_fields(mapper_config.source_type)
        target_type_fields = self._get_fields(mapper_config.target_type)

        extra_field_names = list(
            set(target_type_fields)
            - set(source_type_fields)
            - set(fields_mapping)
        )
        return extra_field_names

    @staticmethod
    def _get_fields(cls: Type[Any]) -> list[str]:
        if is_dataclass(cls):
            return [f.name for f in fields(cls)]
        elif isclass(cls) and issubclass(cls, BaseModel):
            return list(cls.__annotations__.keys())
        else:
            raise TypeError(f'The mapper does not work with the "{cls}" type')

    @staticmethod
    def _create_extra_fields_mapping(
        extra_field_names: list[str],
    ) -> dict[str, FromExtra]:
        extra_fields_mapping = {
            extra_field_name: from_extra(extra_field_name)
            for extra_field_name in extra_field_names
        }
        return extra_fields_mapping

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
    class CommentSource:
        code: str

    @dataclass
    class Comment:
        text: str
        source: CommentSource

    @dataclass
    class Address:
        street: str

    @dataclass
    class Person:
        id: int
        name: str
        age: int
        address: Address
        # friends: list['Person'] TODO:
        comments: list[Comment]

    @dataclass
    class ContactCommentSource:
        code: str

    @dataclass
    class ContactComment:
        text: str
        source: ContactCommentSource

    @dataclass
    class ContactAddress:
        street: str

    @dataclass
    class Contact:
        id: int
        title: str
        slug: str
        created_at: datetime
        address: ContactAddress
        # friends: list['Contact'] TODO:
        comments: list[ContactComment]

    contact_comment_source_mapper_config = MapperConfig(
        source_type=CommentSource,
        target_type=ContactCommentSource,
    )

    contact_comment_mapper_config = MapperConfig(
        source_type=Comment,
        target_type=ContactComment,
        nested_mapper_configs=[contact_comment_source_mapper_config],
    )

    contact_address_mapper_config = MapperConfig(
        source_type=Address,
        target_type=ContactAddress,
    )

    contact_mapper_config = MapperConfig(
        source_type=Person,
        target_type=Contact,
        field_mappings={'title': 'name'},
        computed_fields={'slug': lambda source: f'{source.id}_{source.name}'},
        nested_mapper_configs=[
            contact_address_mapper_config,
            contact_comment_mapper_config,
        ],
    )
    contact_mapper = MapperImpl(mapper_config=contact_mapper_config)

    person = Person(
        id=1,
        name='test_name',
        age=20,
        address=Address(street='test_street'),
        # friends=[
        #     Person(
        #         id=2,
        #         name='test_name',
        #         age=20,
        #         address=Address(street='test_street'),
        #         friends=[],
        #     ),
        # ],
        comments=[
            Comment(
                text='test_text',
                source=CommentSource(
                    code='test_code',
                ),
            ),
        ],
    )

    contact = contact_mapper.map(person, extra={'created_at': datetime.now()})
    print(contact)

    @dataclass
    class Car:
        id: int
        color: str

    class CarInfo(BaseModel):
        color: str

    car_to_car_info_mapper_config = MapperConfig(
        source_type=Car,
        target_type=CarInfo,
    )

    car_to_car_info_mapper = MapperImpl(
        mapper_config=car_to_car_info_mapper_config,
    )

    car = Car(
        id=1,
        color='red',
    )

    car_info = car_to_car_info_mapper.map(car)
    print(car_info)
