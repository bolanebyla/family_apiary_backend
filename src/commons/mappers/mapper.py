from abc import abstractmethod
from typing import Any, Callable, Generic, Iterable, Protocol, Type, TypeVar

T = TypeVar('T')
R = TypeVar('R')
C = TypeVar('C', bound='MapperConfig')


class MapperConfig(Protocol[T, R]):
    source_type: Type[T]
    target_type: Type[R]

    field_mappings: dict[str, str] | None = None
    """Словарь соответствия полей (исходное_поле -> целевое_поле)"""

    computed_fields: dict[str, Callable[[Any], Any]] | None = None
    """Словарь вычисляемых полей (поле -> функция_вычисления)"""

    nested_mappers: list['MapperConfig[Type, Type]'] | None = None
    """Словарь вложенных мапперов для сложных полей (тип поля -> маппер)"""

    def __init__(self) -> None:
        self.field_mappings = self.field_mappings or {}
        self.computed_fields = self.computed_fields or {}
        self.nested_mappers = self.nested_mappers or []


class Mapper(Generic[C, T, R]):
    config: C

    @abstractmethod
    def map(self, source: T, extra: dict[str, Any] | None = None) -> R: ...

    @abstractmethod
    def map_many(
        self, sources: Iterable[T], extra: dict[str, Any] | None = None
    ) -> Iterable[R]: ...
