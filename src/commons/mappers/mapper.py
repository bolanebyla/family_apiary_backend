from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterable, Protocol, Type, TypeVar

T = TypeVar('T')
R = TypeVar('R')
C = TypeVar('C', bound='MapperConfig')


ComputedField = Callable[[Any], Any]  # TODO: добавить более строгое описание


@dataclass(frozen=True)
class MapperConfig(Generic[T, R]):
    source_type: Type[T]
    target_type: Type[R]

    field_mappings: dict[str, str] = field(default_factory=dict)
    """Соответствие названий полей (название_целевого_поля -> название_исходного_поля)"""

    computed_fields: dict[str, ComputedField] = field(default_factory=dict)
    """Вычисляемые поля (название_целевого_поля -> функция_вычисления)"""

    nested_mappers: list['MapperConfig[Type[Any], Type[Any]]'] = field(
        default_factory=list
    )
    """Конфиги мапперов для вложенных классов"""


class Mapper(Generic[C, T, R]):
    config: C

    @abstractmethod
    def map(self, source: T, extra: dict[str, Any] | None = None) -> R: ...

    @abstractmethod
    def map_many(
        self, sources: Iterable[T], extra: dict[str, Any] | None = None
    ) -> Iterable[R]: ...
