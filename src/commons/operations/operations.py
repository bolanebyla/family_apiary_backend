from asyncio import current_task
from contextlib import AsyncExitStack
from contextvars import ContextVar
from functools import wraps
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
)

T = TypeVar('T')
P = ParamSpec('P')


class AsyncOperation:
    """
    Асинхронная операция - контекстный менеджер,
    который позволяет обернуть логическую операцию в единую транзакцию
    """

    def __init__(
        self,
        context_managers: list[AsyncContextManager[Any]] | None = None,
    ):
        if context_managers is None:
            context_managers = []
        self._context_managers = context_managers

        self._context_calls: ContextVar[int] = ContextVar('context_calls')
        self._context_exit_stack: ContextVar[AsyncExitStack] = ContextVar(
            'context_exit_stack'
        )

    async def __aenter__(self) -> None:
        calls_count = self._get_calls_count()

        if calls_count == 0:
            exit_stack = AsyncExitStack()
            self._context_exit_stack.set(exit_stack)
            try:
                await exit_stack.__aenter__()
                for context in self._context_managers:
                    await exit_stack.enter_async_context(context)
            except Exception as exc:
                # TODO: ещё один try
                await exit_stack.__aexit__(type(exc), exc, exc.__traceback__)

        self._context_calls.set(calls_count + 1)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        calls_count = self._get_calls_count() - 1
        self._context_calls.set(calls_count)

        if calls_count != 0:
            return False

        exit_stack = self._context_exit_stack.get()
        # TODO: try
        await exit_stack.__aexit__(exc_type, exc_val, traceback)

        return None

    def _get_calls_count(self) -> int:
        return self._context_calls.get(0)


def async_operation(
    method: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    """
    Декоратор для выполнения тела метода класса в рамках операции.

    Класс должен иметь поле _operation с типом Operation
    """

    # TODO: название аргумента с operation как параметр
    operation_atr_name = '_operation'

    @wraps(method)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if not args:
            raise TypeError(
                '"async_operation" decorator can only be used '
                'with instance methods'
            )

        self = args[0]
        if not hasattr(self, operation_atr_name):
            raise AttributeError(
                f'Class must have "{operation_atr_name}" attribute'
            )

        operation = getattr(self, operation_atr_name)

        if not isinstance(operation, AsyncOperation):
            raise TypeError(
                f'"{operation_atr_name}" must be an AsyncOperation instance'
            )

        async with operation:
            return await method(*args, **kwargs)

    return wrapper
