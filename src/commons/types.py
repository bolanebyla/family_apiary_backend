from contextvars import ContextVar
from typing import Any, Iterable


class ContextBool:
    """
    Булевый тип для текущего контекста выполнения
    """

    def __init__(self, init_value: bool):
        self._context_bool_value: ContextVar[bool] = ContextVar(
            'context_bool_value'
        )
        self._init_value = init_value

    def set(self, value: bool) -> None:
        self._context_bool_value.set(value)

    def set_true(self) -> None:
        self.set(True)

    def set_false(self) -> None:
        self.set(False)

    def __bool__(self) -> bool:
        return self._context_bool_value.get(self._init_value)


class ContextList:
    """
    Список для текущего контекста выполнения
    """

    def __init__(self) -> None:  # TODO: нужен ли None у init для MyPy?
        self._context_list: ContextVar[list[Any]] = ContextVar('context_list')

    def append(self, element: Any) -> None:
        elements_list = self._get_list()
        elements_list.append(element)
        self._context_list.set(elements_list)

    def extend(self, elements: Iterable[Any]) -> None:
        elements_list = self._get_list()
        elements_list.extend(elements)
        self._context_list.set(elements_list)

    def clear(self) -> None:
        self._context_list.set([])

    def __iter__(self) -> Any:
        return iter(self._get_list())

    def _get_list(self) -> list[Any]:
        return self._context_list.get([])
