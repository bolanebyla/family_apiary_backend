from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from inspect import isclass
from typing import Any, Callable, Iterable, Type, cast, get_type_hints

from pydantic import BaseModel, Field, ValidationError, create_model
from pydantic.fields import FieldInfo

from commons.entities.base import create_entity_id
from commons.mappers.mapper import (
    C,
    ComputedField,
    Mapper,
    MapperConfig,
    R,
    T,
)


class PydanticMapper(Mapper[C, T, R]):
    """Реализация маппера с использованием Pydantic"""

    def __init__(self, mapper_config: MapperConfig[T, R]):
        self.mapper_config = mapper_config
        self._init_mapper(mapper_config=mapper_config)

    def _init_mapper(self, mapper_config: MapperConfig[Type, Type]) -> None:
        """Инициализация маппера"""
        try:
            self._init_nested_mapper_configs(
                nested_mapper_configs=mapper_config.nested_mapper_configs,
            )

            # Создаем кэш для вложенных мапперов
            self._nested_mappers = {}
            for nested_config in mapper_config.nested_mapper_configs:
                self._nested_mappers[nested_config.source_type] = (
                    PydanticMapper(nested_config)
                )

            # Создаем динамическую модель Pydantic для маппинга
            self.mapping_model = self._create_mapping_model(mapper_config)

        except Exception as e:
            raise RuntimeError(f'Failed to initialize mapper: {e}')

    def _init_nested_mapper_configs(
        self, nested_mapper_configs: list[MapperConfig[Any, Any]]
    ) -> None:
        """Инициализация вложенных мапперов"""
        for nested_mapper_config in nested_mapper_configs:
            self._init_mapper(mapper_config=nested_mapper_config)

    def _create_mapping_model(
        self, mapper_config: MapperConfig[Type, Type]
    ) -> Type[BaseModel]:
        """Создание динамической модели Pydantic для маппинга"""
        fields_dict = {}

        # Добавляем поля для маппинга
        for target_field, source_field in mapper_config.field_mappings.items():
            field_type = self._get_field_type(
                source_field, mapper_config.source_type
            )
            fields_dict[target_field] = (field_type, Field(alias=source_field))

        # Добавляем вычисляемые поля
        for (
            computed_field_name,
            computed_func,
        ) in mapper_config.computed_fields.items():
            # Для вычисляемых полей используем Any, так как они будут вычисляться динамически
            fields_dict[computed_field_name] = (Any, Field(default=None))

        # Добавляем поля из extra
        extra_field_names = self._get_extra_field_names(mapper_config)
        for extra_field_name in extra_field_names:
            fields_dict[extra_field_name] = (Any, Field(default=None))

        # Создаем модель
        model_name = f'{mapper_config.source_type.__name__}To{mapper_config.target_type.__name__}Mapper'
        return create_model(model_name, **fields_dict)

    def _get_field_type(self, field_name: str, cls: Type[Any]) -> Type[Any]:
        """Получение типа поля"""
        if is_dataclass(cls):
            field_info = next(
                (f for f in fields(cls) if f.name == field_name), None
            )
            if field_info:
                return field_info.type
        elif isclass(cls) and issubclass(cls, BaseModel):
            annotations = get_type_hints(cls)
            return annotations.get(field_name, Any)

        return Any

    def _get_extra_field_names(
        self, mapper_config: MapperConfig[Type, Type]
    ) -> list[str]:
        """Получение имен полей, которые должны быть загружены из extra"""
        target_fields = self._get_fields(mapper_config.target_type)
        source_fields = self._get_fields(mapper_config.source_type)
        mapped_fields = set(mapper_config.field_mappings.keys())
        computed_fields = set(mapper_config.computed_fields.keys())

        return list(
            set(target_fields)
            - set(source_fields)
            - mapped_fields
            - computed_fields
        )

    @staticmethod
    def _get_fields(cls: Type[Any]) -> list[str]:
        """Получение списка полей класса"""
        if is_dataclass(cls):
            # Получаем все поля, включая наследуемые
            all_fields = []
            current_cls = cls

            # Проходим по иерархии наследования
            while current_cls is not None:
                if is_dataclass(current_cls):
                    all_fields.extend([f.name for f in fields(current_cls)])
                current_cls = (
                    current_cls.__bases__[0] if current_cls.__bases__ else None
                )

                # Останавливаемся на object
                if current_cls is object:
                    break

            return list(
                dict.fromkeys(all_fields)
            )  # Убираем дубликаты, сохраняя порядок
        elif isclass(cls) and issubclass(cls, BaseModel):
            return list(cls.__annotations__.keys())
        else:
            raise TypeError(f'The mapper does not work with the "{cls}" type')

    def map(
        self,
        source: T,
        extra: dict[str, Any] | None = None,
    ) -> R:
        """Маппинг одного объекта"""
        try:
            # Преобразуем объект в словарь
            source_dict = self._object_to_dict(source)

            # Получаем поля целевого типа
            target_fields = self._get_fields(self.mapper_config.target_type)

            # Применяем маппинг полей
            mapped_dict = {}

            # Копируем поля с переименованием
            for (
                target_field,
                source_field,
            ) in self.mapper_config.field_mappings.items():
                if (
                    source_field in source_dict
                    and target_field in target_fields
                ):
                    mapped_dict[target_field] = source_dict[source_field]

            # Копируем остальные поля, которые есть в целевом типе
            for field_name, value in source_dict.items():
                if (
                    field_name not in self.mapper_config.field_mappings.values()
                    and field_name in target_fields
                ):
                    mapped_dict[field_name] = value

            # Применяем вычисляемые поля - передаем исходный объект
            for (
                computed_field_name,
                computed_func,
            ) in self.mapper_config.computed_fields.items():
                if computed_field_name in target_fields:
                    mapped_dict[computed_field_name] = computed_func(source)

            # Добавляем поля из extra, которые есть в целевом типе
            if extra:
                for field_name, value in extra.items():
                    if field_name in target_fields:
                        mapped_dict[field_name] = value

            # Обрабатываем вложенные объекты
            self._process_nested_objects(mapped_dict)

            # Создаем целевой объект
            return self.mapper_config.target_type(**mapped_dict)

        except ValidationError as e:
            raise ValueError(f'Validation error during mapping: {e}')
        except Exception as e:
            raise RuntimeError(f'Mapping error: {e}')

    def _process_nested_objects(self, mapped_dict: dict[str, Any]) -> None:
        """Обработка вложенных объектов"""
        for field_name, value in list(mapped_dict.items()):
            if isinstance(value, list):
                # Обрабатываем списки
                mapped_dict[field_name] = [
                    self._map_nested_object(item, field_name) for item in value
                ]
            else:
                # Обрабатываем одиночные объекты
                mapped_value = self._map_nested_object(value, field_name)
                if mapped_value is not None:
                    mapped_dict[field_name] = mapped_value

    def _map_nested_object(self, obj: Any, field_name: str = None) -> Any:
        """Маппинг вложенного объекта"""
        if obj is None:
            return None

        obj_type = type(obj)
        if obj_type in self._nested_mappers:
            # Для вложенных объектов создаем extra с базовыми полями сущности
            extra = {
                'id': create_entity_id(),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            return self._nested_mappers[obj_type].map(obj, extra=extra)

        return obj

    def map_many(
        self,
        sources: Iterable[T],
        extra: dict[str, Any] | None = None,
    ) -> list[R]:
        """Маппинг множества объектов"""
        return [self.map(source, extra) for source in sources]

    def _object_to_dict(self, obj: Any) -> dict[str, Any]:
        """Преобразование объекта в словарь"""
        if is_dataclass(obj):
            return {
                field.name: getattr(obj, field.name) for field in fields(obj)
            }
        elif isinstance(obj, BaseModel):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError(
                f'Cannot convert object of type {type(obj)} to dict'
            )


if __name__ == '__main__':
    # Пример использования
    from dataclasses import dataclass
    from datetime import datetime

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
        comments: list[ContactComment]

    # Конфигурация маппера
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
        computed_fields={
            'slug': lambda source: f'{source["id"]}_{source["name"]}'
        },
        nested_mapper_configs=[
            contact_address_mapper_config,
            contact_comment_mapper_config,
        ],
    )

    contact_mapper = PydanticMapper(mapper_config=contact_mapper_config)

    person = Person(
        id=1,
        name='test_name',
        age=20,
        address=Address(street='test_street'),
        comments=[
            Comment(
                text='test_text',
                source=CommentSource(code='test_code'),
            ),
        ],
    )

    contact = contact_mapper.map(person, extra={'created_at': datetime.now()})
    print(contact)
