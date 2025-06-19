# Mapper

Модуль для маппинга объектов между различными типами данных: dataclass, pydantic. 
Имеет поддержку вложенных типов и списков объектов. Потокобезопаен.

## Принцип работы

### Основная концепция

Маппер позволяет преобразовывать объекты одного типа в объекты другого типа с возможностью:
- Переименования полей
- Вычисления новых полей
- Маппинга вложенных объектов
- Добавления дополнительных полей

### Архитектура

#### Компоненты
- `ObjectTypeDetector` - определение типов объектов
- `ObjectConverter` - конвертация объектов в словари
- `FieldExtractor` - извлечение полей из классов
- `FieldMapper` - маппинг полей между объектами
- `ComputedFieldProcessor` - обработка вычисляемых полей
- `ExtraFieldProcessor` - обработка дополнительных полей
- `NestedObjectProcessor` - обработка вложенных объектов
- `NestedMapperInitializer` - инициализация вложенных мапперов
- `ObjectValidator` - валидация результатов маппинга

### Поддерживаемые типы объектов

- **Dataclass** - стандартные Python dataclass
- **Pydantic** - модели Pydantic
- **Dict-like** - объекты с атрибутом `__dict__`

### Процесс маппинга

1. **Инициализация** - создание вложенных мапперов
2. **Конвертация** - преобразование исходного объекта в словарь
3. **Извлечение полей** - получение списка полей целевого типа
4. **Маппинг полей** - копирование и переименование полей
5. **Вычисляемые поля** - применение функций вычисления
6. **Дополнительные поля** - добавление полей из `extra`
7. **Вложенные объекты** - рекурсивный маппинг вложенных структур
8. **Валидация** - создание целевого объекта

## Иерархия ошибок

### Базовая структура

```python
MapperError (базовый)
├── MapperObjectTypeError (объекты в map())
├── MapperConfigTypeError (типы в конфигурации)
├── FieldExtractionError (извлечение полей)
├── ObjectConversionError (конвертация)
├── FieldMappingError (маппинг полей)
├── ComputedFieldError (вычисляемые поля)
├── NestedMappingError (вложенные объекты)
└── ValidationMappingError (валидация)
```

### Детальное описание ошибок

#### 1. **MapperObjectTypeError**
**Назначение**: Ошибки при определении типа объекта, переданного в метод `map()`

**Где возникает**: 
- `ObjectTypeDetector.detect_type()`
- `ObjectTypeDetector.validate_object_type()`

**Пример**:
```python
try:
    mapper.map("строка", config)  # Неподдерживаемый тип
except MapperObjectTypeError as e:
    print(f"Тип объекта: {e.obj_type}")
```

**Сообщение**: `"The mapper does not work with the "<class 'str'>" type"`

#### 2. **MapperConfigTypeError**
**Назначение**: Ошибки при определении типа класса в конфигурации маппера

**Где возникает**: 
- `FieldExtractor.get_fields()` при проверке `source_type` и `target_type`

**Пример**:
```python
class UnsupportedClass:
    pass

config = MapperConfig(source_type=Person, target_type=UnsupportedClass)
try:
    mapper.map(person, config)
except MapperConfigTypeError as e:
    print(f"Тип класса: {e.cls}")
```

**Сообщение**: `"The mapper does not work with the "<class 'UnsupportedClass'>" type in MapperConfig"`

#### 3. **FieldExtractionError**
**Назначение**: Ошибки при извлечении полей из классов

**Где возникает**: 
- `FieldExtractor.get_fields()` при проблемах с рефлексией

**Пример**:
```python
class ProblematicClass:
    field: "NonExistentType"  # Проблемная аннотация

try:
    mapper.map(obj, MapperConfig(source_type=Person, target_type=ProblematicClass))
except FieldExtractionError as e:
    print(f"Класс: {e.cls}, Ошибка: {e.original_error}")
```

**Сообщение**: `"Error extracting fields from <class 'ProblematicClass'>: ..."`

#### 4. **ObjectConversionError**
**Назначение**: Ошибки при конвертации объекта в словарь

**Где возникает**: 
- `ObjectConverter.to_dict()`

**Пример**:
```python
class UnconvertibleObject:
    def __getattr__(self, name):
        raise AttributeError("Cannot access attributes")

try:
    mapper.map(UnconvertibleObject(), config)
except ObjectConversionError as e:
    print(f"Тип объекта: {e.obj_type}, Ошибка: {e.original_error}")
```

**Сообщение**: `"Cannot convert object of type <class 'UnconvertibleObject'> to dict: ..."`

#### 5. **FieldMappingError**
**Назначение**: Ошибки при маппинге полей

**Где возникает**: 
- `FieldMapper.map_fields()`

**Пример**:
```python
config = MapperConfig(
    source_type=Person,
    target_type=Contact,
    field_mappings={'title': 'nonexistent_field'}
)

try:
    mapper.map(person, config)
except FieldMappingError as e:
    print(f"Поле: {e.source_field} -> {e.target_field}")
```

**Сообщение**: `"Failed to map field "nonexistent_field" to "title""`

#### 6. **ComputedFieldError**
**Назначение**: Ошибки при вычислении полей

**Где возникает**: 
- `ComputedFieldProcessor.process_computed_fields()`

**Пример**:
```python
def failing_function(source):
    raise ValueError("Ошибка вычисления")

config = MapperConfig(
    source_type=Person,
    target_type=Contact,
    computed_fields={'slug': failing_function}
)

try:
    mapper.map(person, config)
except ComputedFieldError as e:
    print(f"Поле: {e.field_name}, Ошибка: {e.original_error}")
```

**Сообщение**: `"Error computing field "slug": Ошибка вычисления"`

#### 7. **NestedMappingError**
**Назначение**: Ошибки при маппинге вложенных объектов

**Где возникает**: 
- `NestedObjectProcessor._map_nested_object()`

**Пример**:
```python
@dataclass
class ProblematicAddress:
    street: str
    
    def __post_init__(self):
        if self.street == "problematic":
            raise ValueError("Проблемная улица")

config = MapperConfig(
    source_type=Person,
    target_type=Contact,
    nested_mapper_configs=[address_mapper_config]
)

person.address = ProblematicAddress(street="problematic")
try:
    mapper.map(person, config)
except NestedMappingError as e:
    print(f"Тип объекта: {e.obj_type}, Ошибка: {e.original_error}")
```

**Сообщение**: `"Error mapping nested object of type ProblematicAddress: Проблемная улица"`

#### 8. **ValidationMappingError**
**Назначение**: Ошибки валидации при создании целевого объекта

**Где возникает**: 
- `ObjectValidator.validate_mapping_result()`

**Пример**:
```python
@dataclass
class InvalidContact:
    id: int
    title: str
    # Отсутствует обязательное поле address

config = MapperConfig(source_type=Person, target_type=InvalidContact)

try:
    mapper.map(person, config)
except ValidationMappingError as e:
    print(f"Целевой тип: {e.target_type}, Ошибка: {e.validation_error}")
```

**Сообщение**: `"Validation error creating InvalidContact: ..."`

## Примеры использования

### Базовый маппинг

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Person:
    id: int
    name: str
    age: int

@dataclass
class Contact:
    id: int
    title: str
    slug: str
    created_at: datetime

# Конфигурация маппера
config = MapperConfig(
    source_type=Person,
    target_type=Contact,
    field_mappings={'title': 'name'},
    computed_fields={'slug': lambda source: f'{source.id}_{source.name}'},
)

# Создание маппера
mapper = MapperImpl()

# Маппинг
person = Person(id=1, name='John', age=30)
contact = mapper.map(
    person, 
    config, 
    extra={'created_at': datetime.now()}
)
```

### Маппинг с вложенными объектами

```python
@dataclass
class Address:
    street: str
    city: str

@dataclass
class Person:
    id: int
    name: str
    address: Address

@dataclass
class ContactAddress:
    street: str
    city: str

@dataclass
class Contact:
    id: int
    name: str
    address: ContactAddress

# Конфигурации для вложенных объектов
address_config = MapperConfig(
    source_type=Address,
    target_type=ContactAddress,
)

person_config = MapperConfig(
    source_type=Person,
    target_type=Contact,
    nested_mapper_configs=[address_config],
)

# Маппинг
person = Person(
    id=1, 
    name='John', 
    address=Address(street='Main St', city='New York')
)

contact = mapper.map(person, person_config)
```

### Обработка ошибок

```python
try:
    result = mapper.map(source, config)
except MapperObjectTypeError as e:
    print(f"Неподдерживаемый тип объекта: {e.obj_type}")
except MapperConfigTypeError as e:
    print(f"Неподдерживаемый тип в конфигурации: {e.cls}")
except ComputedFieldError as e:
    print(f"Ошибка в вычисляемом поле {e.field_name}: {e.original_error}")
except NestedMappingError as e:
    print(f"Ошибка вложенного объекта {e.obj_type}: {e.original_error}")
except ValidationMappingError as e:
    print(f"Ошибка валидации {e.target_type}: {e.validation_error}")
except MapperError as e:
    print(f"Общая ошибка маппера: {e}")
```

## Расширение функциональности

### Добавление нового типа объектов

1. Добавить новый тип в `ObjectType` enum:
```python
class ObjectType(StrEnum):
    DATACLASS = auto()
    PYDANTIC = auto()
    DICT_LIKE = auto()
    NEW_TYPE = auto()  # Новый тип
    UNSUPPORTED = auto()
```

2. Обновить `ObjectTypeDetector`:
```python
@staticmethod
def detect_type(obj: Any) -> ObjectType:
    if is_new_type(obj):
        return ObjectType.NEW_TYPE
    # ... остальная логика
```

3. Обновить `ObjectConverter`:
```python
def to_dict(self, obj: Any) -> dict[str, Any]:
    obj_type = self._type_detector.detect_type(obj)
    
    if obj_type == ObjectType.NEW_TYPE:
        return convert_new_type_to_dict(obj)
    # ... остальная логика
```

## Принципы проектирования

### 1. **Composition over Inheritance**
Предпочтение композиции над наследованием для гибкости и тестируемости.

### 2. **Dependency Injection**
Зависимости передаются через конструкторы для лучшей тестируемости.

### 3. **Fail Fast**
Ошибки обнаруживаются как можно раньше с информативными сообщениями.

### 4. **Separation of Concerns**
Каждый класс отвечает за одну конкретную задачу.

### 5. **Error Context Preservation**
Сохранение контекста ошибок для лучшей отладки.

## Тестирование

Модуль спроектирован для легкого тестирования:

- Каждый класс можно тестировать независимо
- Зависимости можно мокать через конструкторы
- Кастомные ошибки предоставляют богатый контекст для тестов
## Производительность

- Кэширование вложенных мапперов
- Эффективная детекция типов
- Минимальное количество итераций по полям
- Ленивая инициализация компонентов 