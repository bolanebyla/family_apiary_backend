from dataclasses import fields, is_dataclass
from enum import StrEnum, auto
from inspect import isclass
from typing import Any, Iterable, Type, get_type_hints

from pydantic import BaseModel, ValidationError

from commons.mappers.mapper import (
    C,
    Mapper,
    MapperConfig,
    R,
    T,
)


class MapperError(Exception):
    """Базовый класс для всех ошибок маппера"""

    pass


class MapperObjectTypeError(MapperError):
    """Ошибка при определении типа объекта, переданного в метод маппера"""

    def __init__(self, obj: Any, message: str | None = None):
        self.obj = obj
        self.obj_type = type(obj)
        super().__init__(
            message
            or f'The mapper does not work with the "{self.obj_type}" type'
        )


class MapperConfigTypeError(MapperError):
    """Ошибка при определении типа класса в конфигурации маппера"""

    def __init__(self, cls: Type[Any], message: str | None = None):
        self.cls = cls
        super().__init__(
            message
            or f'The mapper does not work with the "{cls}" type in MapperConfig'
        )


class FieldExtractionError(MapperError):
    """Ошибка при извлечении полей из класса"""

    def __init__(self, cls: Type[Any], original_error: Exception):
        self.cls = cls
        self.original_error = original_error
        super().__init__(
            f'Error extracting fields from {cls}: {original_error}'
        )


class ObjectConversionError(MapperError):
    """Ошибка при конвертации объекта в словарь"""

    def __init__(self, obj: Any, original_error: Exception | None = None):
        self.obj = obj
        self.obj_type = type(obj)
        self.original_error = original_error

        message = f'Cannot convert object of type {self.obj_type} to dict'
        if original_error:
            message += f': {original_error}'

        super().__init__(message)


class FieldMappingError(MapperError):
    """Ошибка при маппинге полей"""

    def __init__(
        self, source_field: str, target_field: str, message: str | None = None
    ):
        self.source_field = source_field
        self.target_field = target_field
        super().__init__(
            message
            or f'Failed to map field "{source_field}" to "{target_field}"'
        )


class ComputedFieldError(MapperError):
    """Ошибка при вычислении поля"""

    def __init__(self, field_name: str, original_error: Exception):
        self.field_name = field_name
        self.original_error = original_error
        super().__init__(
            f'Error computing field "{field_name}": {original_error}'
        )


class NestedMappingError(MapperError):
    """Ошибка при маппинге вложенных объектов"""

    def __init__(self, obj_type: Type[Any], original_error: Exception):
        self.obj_type = obj_type
        self.original_error = original_error
        super().__init__(
            f'Error mapping nested object of type {obj_type.__name__}: {original_error}'
        )


class ValidationMappingError(MapperError):
    """Ошибка валидации при создании целевого объекта"""

    def __init__(
        self, target_type: Type[Any], validation_error: ValidationError
    ):
        self.target_type = target_type
        self.validation_error = validation_error
        super().__init__(
            f'Validation error creating {target_type.__name__}: {validation_error}'
        )


class ObjectType(StrEnum):
    """Типы объектов, поддерживаемые маппером"""

    DATACLASS = auto()
    PYDANTIC = auto()
    DICT_LIKE = auto()
    UNSUPPORTED = auto()


class ObjectTypeDetector:
    """Детектор типов объектов"""

    @staticmethod
    def detect_type(obj: Any) -> ObjectType:
        """Определяет тип объекта"""
        if is_dataclass(obj):
            return ObjectType.DATACLASS
        elif isinstance(obj, BaseModel):
            return ObjectType.PYDANTIC
        elif hasattr(obj, '__dict__'):
            return ObjectType.DICT_LIKE
        else:
            return ObjectType.UNSUPPORTED

    @staticmethod
    def detect_class_type(cls: Type[Any]) -> ObjectType:
        """Определяет тип класса"""
        if is_dataclass(cls):
            return ObjectType.DATACLASS
        elif isclass(cls) and issubclass(cls, BaseModel):
            return ObjectType.PYDANTIC
        elif hasattr(cls, '__dict__'):
            return ObjectType.DICT_LIKE
        else:
            return ObjectType.UNSUPPORTED

    @staticmethod
    def validate_object_type(obj: Any) -> None:
        """Проверяет, поддерживается ли тип объекта"""
        obj_type = ObjectTypeDetector.detect_type(obj)
        if obj_type == ObjectType.UNSUPPORTED:
            raise MapperObjectTypeError(obj)

    @staticmethod
    def validate_class_type(cls: Type[Any]) -> None:
        """Проверяет, поддерживается ли тип класса"""
        cls_type = ObjectTypeDetector.detect_class_type(cls)
        if cls_type == ObjectType.UNSUPPORTED:
            raise MapperConfigTypeError(cls)


class ObjectConverter:
    """Универсальный конвертер объектов в словари"""

    def __init__(self, type_detector: ObjectTypeDetector):
        self._type_detector = type_detector

    def to_dict(self, obj: Any) -> dict[str, Any]:
        """Конвертирует объект в словарь"""
        try:
            self._type_detector.validate_object_type(obj)
            obj_type = self._type_detector.detect_type(obj)

            if obj_type == ObjectType.DATACLASS:
                return {
                    field.name: getattr(obj, field.name)
                    for field in fields(obj)
                }
            elif obj_type == ObjectType.PYDANTIC:
                return obj.dict()
            elif obj_type == ObjectType.DICT_LIKE:
                return obj.__dict__
            else:
                raise ObjectConversionError(obj)
        except MapperError:
            raise
        except Exception as e:
            raise ObjectConversionError(obj, e)


class FieldTypeResolver:
    """Резолвер типов полей"""

    def __init__(self, type_detector: ObjectTypeDetector):
        self._type_detector = type_detector

    def get_field_type(self, field_name: str, cls: Type[Any]) -> Type[Any]:
        """Получает тип поля"""
        cls_type = self._type_detector.detect_class_type(cls)

        if cls_type == ObjectType.DATACLASS:
            field_info = next(
                (f for f in fields(cls) if f.name == field_name), None
            )
            if field_info:
                return field_info.type
        elif cls_type == ObjectType.PYDANTIC:
            annotations = get_type_hints(cls)
            return annotations.get(field_name, Any)

        return Any


class FieldExtractor:
    """Извлекатель полей из классов"""

    def __init__(self, type_detector: ObjectTypeDetector):
        self._type_detector = type_detector

    def get_fields(self, cls: Type[Any]) -> list[str]:
        """Получает список полей класса"""
        try:
            self._type_detector.validate_class_type(cls)
            cls_type = self._type_detector.detect_class_type(cls)

            if cls_type == ObjectType.DATACLASS:
                return self._get_dataclass_fields(cls)
            elif cls_type == ObjectType.PYDANTIC:
                return list(cls.__annotations__.keys())
            else:
                raise MapperConfigTypeError(cls)
        except MapperError:
            raise
        except Exception as e:
            raise FieldExtractionError(cls, e)

    @staticmethod
    def _get_dataclass_fields(cls: Type[Any]) -> list[str]:
        """Получает поля dataclass с учетом наследования"""
        all_fields = []
        current_cls = cls

        while current_cls is not None and current_cls is not object:
            if is_dataclass(current_cls):
                all_fields.extend([f.name for f in fields(current_cls)])
            current_cls = (
                current_cls.__bases__[0] if current_cls.__bases__ else None
            )

        return list(
            dict.fromkeys(all_fields)
        )  # Убираем дубликаты, сохраняя порядок


class FieldMapper:
    """Маппер полей"""

    def __init__(self, field_extractor: FieldExtractor):
        self._field_extractor = field_extractor

    def map_fields(
        self,
        source_dict: dict[str, Any],
        mapper_config: MapperConfig[Type, Type],
        target_fields: list[str],
    ) -> dict[str, Any]:
        """Маппит поля из исходного объекта в целевой"""
        mapped_dict = {}

        # Копируем поля с переименованием
        for target_field, source_field in mapper_config.field_mappings.items():
            if source_field in source_dict and target_field in target_fields:
                mapped_dict[target_field] = source_dict[source_field]

        # Копируем остальные поля, которые есть в целевом типе
        for field_name, value in source_dict.items():
            if (
                field_name not in mapper_config.field_mappings.values()
                and field_name in target_fields
            ):
                mapped_dict[field_name] = value

        return mapped_dict


class ComputedFieldProcessor:
    """Обработчик вычисляемых полей"""

    def process_computed_fields(
        self,
        source: Any,
        mapper_config: MapperConfig[Type, Type],
        target_fields: list[str],
    ) -> dict[str, Any]:
        """Обрабатывает вычисляемые поля"""
        computed_dict = {}

        for (
            computed_field_name,
            computed_func,
        ) in mapper_config.computed_fields.items():
            if computed_field_name in target_fields:
                try:
                    computed_dict[computed_field_name] = computed_func(source)
                except Exception as e:
                    raise ComputedFieldError(computed_field_name, e)

        return computed_dict


class ExtraFieldProcessor:
    """Обработчик дополнительных полей"""

    def __init__(self, field_extractor: FieldExtractor):
        self._field_extractor = field_extractor

    def process_extra_fields(
        self,
        extra: dict[str, Any] | None,
        mapper_config: MapperConfig[Type, Type],
    ) -> dict[str, Any]:
        """Обрабатывает дополнительные поля"""
        if not extra:
            return {}

        target_fields = self._field_extractor.get_fields(
            mapper_config.target_type
        )
        extra_dict = {}

        for field_name, value in extra.items():
            if field_name in target_fields:
                extra_dict[field_name] = value

        return extra_dict


class NestedObjectProcessor:
    """Обработчик вложенных объектов"""

    def __init__(
        self, mapper: 'MapperImpl', nested_mappers: dict[Type, 'MapperImpl']
    ):
        self._mapper = mapper
        self._nested_mappers = nested_mappers

    def process_nested_objects(
        self,
        mapped_dict: dict[str, Any],
        mapper_config: MapperConfig[Type, Type],
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Обрабатывает вложенные объекты"""
        for field_name, value in list(mapped_dict.items()):
            if isinstance(value, list):
                mapped_dict[field_name] = [
                    self._map_nested_object(
                        item, field_name, mapper_config, extra
                    )
                    for item in value
                ]
            else:
                mapped_value = self._map_nested_object(
                    value, field_name, mapper_config, extra
                )
                if mapped_value is not None:
                    mapped_dict[field_name] = mapped_value

    def _map_nested_object(
        self,
        obj: Any,
        field_name: str = None,
        mapper_config: MapperConfig[Type, Type] = None,
        extra: dict[str, Any] | None = None,
    ) -> Any:
        """Маппит вложенный объект"""
        if obj is None:
            return None

        obj_type = type(obj)
        nested_mapper = self._nested_mappers.get(obj_type)

        if nested_mapper is not None:
            nested_config = next(
                (
                    config
                    for config in mapper_config.nested_mapper_configs
                    if config.source_type == obj_type
                ),
                None,
            )

            if nested_config:
                try:
                    return nested_mapper.map(obj, nested_config, extra=extra)
                except MapperError:
                    raise
                except Exception as e:
                    raise NestedMappingError(obj_type, e)

        return obj


class NestedMapperInitializer:
    """Инициализатор вложенных мапперов"""

    def initialize_nested_mappers(
        self,
        nested_mapper_configs: list[MapperConfig[Any, Any]],
        nested_mappers: dict[Type, 'MapperImpl'],
    ) -> None:
        """Инициализирует вложенные мапперы"""
        for nested_mapper_config in nested_mapper_configs:
            if nested_mapper_config.source_type not in nested_mappers:
                nested_mappers[nested_mapper_config.source_type] = MapperImpl()


class ObjectValidator:
    """Валидатор объектов"""

    @staticmethod
    def validate_mapping_result(
        mapped_dict: dict[str, Any], target_type: Type[Any]
    ) -> None:
        """Валидирует результат маппинга"""
        try:
            target_type(**mapped_dict)
        except ValidationError as e:
            raise ValidationMappingError(target_type, e)
        except Exception as e:
            raise ValidationMappingError(
                target_type,
                ValidationError.from_exception_data(
                    'ValidationError',
                    [{'loc': (), 'msg': str(e), 'type': 'value_error'}],
                ),
            )


class MapperImpl(Mapper):
    """
    Реализация маппера

    Поддерживает мапинг датаклассов и pydantic моделей.
    Для маппинга используется Pydantic.
    """

    def __init__(self):
        # Инициализация зависимостей
        self._type_detector = ObjectTypeDetector()
        self._converter = ObjectConverter(self._type_detector)
        self._field_extractor = FieldExtractor(self._type_detector)
        self._field_mapper = FieldMapper(self._field_extractor)
        self._computed_field_processor = ComputedFieldProcessor()
        self._extra_field_processor = ExtraFieldProcessor(self._field_extractor)
        self._nested_mapper_initializer = NestedMapperInitializer()
        self._object_validator = ObjectValidator()

    def map(
        self,
        source: T,
        mapper_config: C,
        extra: dict[str, Any] | None = None,
    ) -> R:
        """Маппинг одного объекта"""
        try:
            # Создаем локальный кэш для вложенных мапперов
            nested_mappers = {}

            # Инициализируем вложенные мапперы
            self._nested_mapper_initializer.initialize_nested_mappers(
                nested_mapper_configs=mapper_config.nested_mapper_configs,
                nested_mappers=nested_mappers,
            )

            # Создаем процессор вложенных объектов с локальным кэшем
            nested_object_processor = NestedObjectProcessor(
                self, nested_mappers
            )

            # Преобразуем объект в словарь
            source_dict = self._converter.to_dict(source)

            # Получаем поля целевого типа
            target_fields = self._field_extractor.get_fields(
                mapper_config.target_type
            )

            # Применяем маппинг полей
            mapped_dict = self._field_mapper.map_fields(
                source_dict, mapper_config, target_fields
            )

            # Применяем вычисляемые поля
            computed_dict = (
                self._computed_field_processor.process_computed_fields(
                    source, mapper_config, target_fields
                )
            )
            mapped_dict.update(computed_dict)

            # Добавляем поля из extra
            extra_dict = self._extra_field_processor.process_extra_fields(
                extra, mapper_config
            )
            mapped_dict.update(extra_dict)

            # Обрабатываем вложенные объекты
            nested_object_processor.process_nested_objects(
                mapped_dict, mapper_config, extra
            )

            # Создаем целевой объект
            return mapper_config.target_type(**mapped_dict)

        except MapperError:
            # Пробрасываем кастомные ошибки маппера
            raise
        except Exception as e:
            # Оборачиваем неожиданные ошибки в базовую ошибку маппера
            raise MapperError(f'Unexpected error during mapping: {e}') from e

    def map_many(
        self,
        sources: Iterable[T],
        mapper_config: C,
        extra: dict[str, Any] | None = None,
    ) -> list[R]:
        """Маппинг множества объектов"""
        return [self.map(source, mapper_config, extra) for source in sources]


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
        computed_fields={'slug': lambda source: f'{source.id}_{source.name}'},
        nested_mapper_configs=[
            contact_address_mapper_config,
            contact_comment_mapper_config,
        ],
    )

    contact_mapper = MapperImpl()

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

    # Успешный маппинг
    try:
        contact = contact_mapper.map(
            person, contact_mapper_config, extra={'created_at': datetime.now()}
        )
        print('Успешный маппинг:', contact)
    except MapperError as e:
        print(f'Ошибка маппера: {e}')

    # Пример обработки кастомных ошибок
    print('\n--- Примеры кастомных ошибок ---')

    # 1. Ошибка неподдерживаемого типа объекта
    # Возникает в ObjectTypeDetector.detect_type() при проверке объекта, переданного в map()
    try:
        unsupported_obj = 'простая строка'
        contact_mapper.map(unsupported_obj, contact_mapper_config)
    except MapperObjectTypeError as e:
        print(f'MapperObjectTypeError: {e}')
        print(f'  Тип объекта: {e.obj_type}')

    # 1a. Ошибка неподдерживаемого типа класса (в FieldExtractor)
    # Возникает в FieldExtractor.get_fields() при проверке типов в MapperConfig
    class UnsupportedClass:
        """Класс, который не является dataclass, pydantic моделью или dict-like"""

        pass

    unsupported_class_mapper_config = MapperConfig(
        source_type=Person,
        target_type=UnsupportedClass,  # Неподдерживаемый тип класса
    )

    try:
        contact_mapper.map(person, unsupported_class_mapper_config)
    except MapperConfigTypeError as e:
        print(f'MapperConfigTypeError: {e}')
        print(f'  Тип класса: {e.cls}')

    # 1b. Ошибка извлечения полей из класса
    # Возникает в FieldExtractor.get_fields() при проблемах с рефлексией
    class ProblematicClass:
        """Класс с проблемами в аннотациях типов"""

        def __init__(self):
            self.normal_field = 'normal'

        # Проблемная аннотация, которая может вызвать ошибку при get_type_hints
        problematic_field: 'NonExistentType'  # type: ignore

        @property
        def property_field(self):
            return 'property'

    # Создаем проблемную ситуацию, которая может вызвать ошибку при извлечении полей
    problematic_class_mapper_config = MapperConfig(
        source_type=Person,
        target_type=ProblematicClass,
    )

    try:
        contact_mapper.map(person, problematic_class_mapper_config)
    except FieldExtractionError as e:
        print(f'FieldExtractionError: {e}')
        print(f'  Класс: {e.cls}')
        print(f'  Исходная ошибка: {e.original_error}')
    except MapperError as e:
        print(f'MapperError: {e}')

    # 1c. Альтернативный пример FieldExtractionError - класс с проблемами в dataclass
    @dataclass
    class BrokenDataclass:
        """Dataclass с проблемами, которые вызовут ошибку при извлечении полей"""

        normal_field: str

        def __post_init__(self):
            # Имитируем проблему при инициализации dataclass
            if self.normal_field == 'break':
                # Это вызовет ошибку при попытке получить поля через fields()
                raise RuntimeError('Dataclass is broken!')

    # Создаем экземпляр, который вызовет проблему
    try:
        broken_dataclass_mapper_config = MapperConfig(
            source_type=Person,
            target_type=BrokenDataclass,
        )

        contact_mapper.map(person, broken_dataclass_mapper_config)
    except FieldExtractionError as e:
        print(f'FieldExtractionError (dataclass): {e}')
        print(f'  Класс: {e.cls}')
        print(f'  Исходная ошибка: {e.original_error}')
    except MapperError as e:
        print(f'MapperError: {e}')

    # 2. Ошибка вычисляемого поля
    def failing_computed_field(source):
        raise ValueError('Ошибка в вычисляемом поле')

    failing_mapper_config = MapperConfig(
        source_type=Person,
        target_type=Contact,
        computed_fields={'slug': failing_computed_field},
    )

    try:
        contact_mapper.map(person, failing_mapper_config)
    except ComputedFieldError as e:
        print(f'ComputedFieldError: {e}')
        print(f'  Поле: {e.field_name}')
        print(f'  Исходная ошибка: {e.original_error}')

    # 3. Ошибка вложенного маппинга
    @dataclass
    class ProblematicAddress:
        street: str

    @dataclass
    class ProblematicContactAddress:
        street: str

        def __post_init__(self):
            # Ошибка возникает при создании целевого объекта
            if self.street == 'problematic_street':
                raise ValueError('Проблемная улица!')

    # Конфигурация маппера для проблемного адреса
    problematic_address_mapper_config = MapperConfig(
        source_type=ProblematicAddress,
        target_type=ProblematicContactAddress,
    )

    problematic_person = Person(
        id=1,
        name='test',
        age=20,
        address=ProblematicAddress(
            street='problematic_street'
        ),  # Нормальное создание
        comments=[],
    )

    # Конфигурация с проблемным вложенным маппером
    problematic_contact_mapper_config = MapperConfig(
        source_type=Person,
        target_type=Contact,
        field_mappings={'title': 'name'},
        computed_fields={'slug': lambda source: f'{source.id}_{source.name}'},
        nested_mapper_configs=[problematic_address_mapper_config],
    )

    try:
        contact_mapper.map(
            problematic_person,
            problematic_contact_mapper_config,
            extra={'created_at': datetime.now()},
        )
    except NestedMappingError as e:
        print(f'NestedMappingError: {e}')
        print(f'  Тип объекта: {e.obj_type}')
        print(f'  Исходная ошибка: {e.original_error}')
    except MapperError as e:
        print(f'MapperError: {e}')

    # 3a. Альтернативный пример NestedMappingError - ошибка в процессе маппинга
    @dataclass
    class ComplexAddress:
        street: str
        city: str

    @dataclass
    class ComplexContactAddress:
        street: str
        city: str

    def problematic_mapping_function(source):
        # Имитируем ошибку в процессе маппинга
        if source.street == 'error_street':
            raise RuntimeError('Ошибка в процессе маппинга адреса')
        return source.street

    complex_address_mapper_config = MapperConfig(
        source_type=ComplexAddress,
        target_type=ComplexContactAddress,
        computed_fields={'street': problematic_mapping_function},
    )

    complex_person = Person(
        id=1,
        name='test',
        age=20,
        address=ComplexAddress(street='error_street', city='test_city'),
        comments=[],
    )

    complex_contact_mapper_config = MapperConfig(
        source_type=Person,
        target_type=Contact,
        field_mappings={'title': 'name'},
        computed_fields={'slug': lambda source: f'{source.id}_{source.name}'},
        nested_mapper_configs=[complex_address_mapper_config],
    )

    try:
        contact_mapper.map(
            complex_person,
            complex_contact_mapper_config,
            extra={'created_at': datetime.now()},
        )
    except NestedMappingError as e:
        print(f'NestedMappingError (альтернативный): {e}')
        print(f'  Тип объекта: {e.obj_type}')
        print(f'  Исходная ошибка: {e.original_error}')
    except MapperError as e:
        print(f'MapperError: {e}')

    # 4. Ошибка валидации
    @dataclass
    class InvalidContact:
        id: int
        title: str
        slug: str
        created_at: datetime
        # Отсутствует обязательное поле address
        comments: list[ContactComment]

    invalid_contact_mapper_config = MapperConfig(
        source_type=Person,
        target_type=InvalidContact,
        field_mappings={'title': 'name'},
        computed_fields={'slug': lambda source: f'{source.id}_{source.name}'},
    )

    try:
        contact_mapper.map(
            person,
            invalid_contact_mapper_config,
            extra={'created_at': datetime.now()},
        )
    except ValidationMappingError as e:
        print(f'ValidationMappingError: {e}')
        print(f'  Целевой тип: {e.target_type}')
        print(f'  Ошибка валидации: {e.validation_error}')
    except MapperError as e:
        print(f'MapperError: {e}')

    print('\n--- Конец примеров ---')
