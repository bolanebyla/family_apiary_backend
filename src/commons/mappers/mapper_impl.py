from dataclasses import Field, dataclass, fields
from datetime import datetime
from typing import Any, ClassVar, Iterable, Protocol, Type

from dataclass_mapper import create_mapper, from_extra, map_to
from dataclass_mapper.special_field_mappings import FromExtra

from commons.mappers.mapper import C, ComputedField, Mapper, MapperConfig, R, T


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


FieldsMapping = dict[str, str | ComputedField | FromExtra]


class MapperImpl(Mapper[C, T, R]):
    def __init__(self, mapper_config: MapperConfig[T, R]):
        self.mapper_config = mapper_config

        self._init_mapper(mapper_config=mapper_config)

    def _init_mapper(
        self,
        mapper_config: MapperConfig[DataclassInstance, DataclassInstance],
    ) -> None:
        for nested_mapper_config in mapper_config.nested_mappers:
            self._init_mapper(mapper_config=nested_mapper_config)

        fields_mapping = self._create_fields_mapping(mapper_config)

        create_mapper(
            SourceCls=mapper_config.source_type,
            TargetCls=mapper_config.target_type,
            mapping=fields_mapping,
        )

    def _create_fields_mapping(
        self,
        mapper_config: MapperConfig[DataclassInstance, DataclassInstance],
    ) -> FieldsMapping:
        fields_mapping = (
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
        mapper_config: MapperConfig[DataclassInstance, DataclassInstance],
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
    def _get_fields(cls: Type[DataclassInstance]) -> list[str]:
        return [f.name for f in fields(cls)]

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

    class ContactCommentSourceMapperConfig(
        MapperConfig[CommentSource, ContactCommentSource]
    ):
        source_type = CommentSource
        target_type = ContactCommentSource

    class ContactCommentMapperConfig(MapperConfig[Comment, ContactComment]):
        source_type = Comment
        target_type = ContactComment

        nested_mappers = [ContactCommentSourceMapperConfig()]

    class ContactAddressMapperConfig(MapperConfig[Address, ContactAddress]):
        source_type = Address
        target_type = ContactAddress

    class ContactMapperConfig(MapperConfig[Person, Contact]):
        source_type = Person
        target_type = Contact

        field_mappings = {'title': 'name'}
        computed_fields = {'slug': lambda source: f'{source.id}_{source.name}'}
        nested_mappers = [
            ContactAddressMapperConfig(),
            ContactCommentMapperConfig(),
        ]

    contact_mapper_config = ContactMapperConfig()
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
