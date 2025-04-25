import inspect
from abc import abstractmethod
from typing import Any, Type

from dishka import AsyncContainer
from typing_extensions import override

from commons.operations.operations import AsyncOperation, async_operation

from .base import (
    CommandHandler,
    CommandMediator,
    QueryHandler,
    QueryMediator,
    TRequest,
    TResult,
    _RequestHandler,
)


def find_subclasses(
    cls: Type[_RequestHandler[TRequest, TResult]],
) -> list[Type[_RequestHandler[TRequest, TResult]]]:
    """
    Возвращает наследников класса
    """
    subclasses = []
    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(
            find_subclasses(subclass)
        )  # Рекурсивно ищем наследников
    return subclasses


def get_handler_request_type(
    handler_cls: Type[_RequestHandler[TRequest, TResult]],
) -> Type[TRequest]:
    """
    Получает тип аргумента метода
    """
    signature = inspect.signature(handler_cls.handle)
    # может быть только один аргумент
    # TODO: выбрасывать ошибку если несколько аргументов
    _, request_parameter = tuple(signature.parameters.items())[-1]
    request_type_annotation: Type[TRequest] = request_parameter.annotation
    return request_type_annotation


class CQRSMediator:
    """
    Медиатор для реализации подхода CQRS.

    Каждый обработчик вызывается в рамках операции (транзакции)
    """

    def __init__(self, container: AsyncContainer, operation: AsyncOperation):
        self._handlers_by_requests: dict[
            Any, Type[_RequestHandler[Any, Any]]
        ] = {}
        self._container = container
        self._operation = operation

    @async_operation
    async def execute_request(self, req: TRequest) -> TResult:
        handler_cls = self._handlers_by_requests.get(req.__class__)
        if not handler_cls:
            # TODO: использовать свою ошибку
            raise ValueError(
                f'Handler for request {type(req)} is not registered'
            )

        async with self._container() as request_container:
            handler: _RequestHandler[
                TRequest, TResult
            ] = await request_container.get(handler_cls)

            return await handler.handle(req)

    def resolve_handlers(self) -> None:
        """
        Находит и регистрирует все обработчики.

        Поиск производится по наследникам от базового обработчика
        """
        # TODO: вынести в атрибуты
        base_request_handler_cls = self.get_base_request_handler_cls()
        handlers_classes = set(find_subclasses(base_request_handler_cls))
        for handler_cls in handlers_classes:
            request_type = get_handler_request_type(handler_cls=handler_cls)

            registered_handler_cls = self._handlers_by_requests.get(
                request_type
            )

            if registered_handler_cls:
                if handler_cls.__name__ == registered_handler_cls.__name__:
                    continue
                # TODO: использовать свою ошибку
                raise ValueError(
                    f'Request {request_type} is already registered '
                    f'in handler {registered_handler_cls}. '
                    f"Can't use it for {handler_cls}"
                )

            self._handlers_by_requests[request_type] = handler_cls

    @abstractmethod
    def get_base_request_handler_cls(
        self,
    ) -> Type[_RequestHandler[Any, Any]]: ...


class QueryMediatorImpl(CQRSMediator, QueryMediator):
    """
    Медиатор для запросов
    """

    @override
    def get_base_request_handler_cls(
        self,
    ) -> Type[QueryHandler[TRequest, TResult]]:
        return QueryHandler

    @override
    async def send(self, query: TRequest) -> TResult:
        result: TResult = await self.execute_request(req=query)
        return result


class CommandMediatorImpl(CQRSMediator, CommandMediator):
    """
    Медиатор для команд
    """

    @override
    def get_base_request_handler_cls(
        self,
    ) -> Type[CommandHandler[TRequest, TResult]]:
        return CommandHandler

    @override
    async def send(self, command: TRequest) -> TResult:
        result: TResult = await self.execute_request(req=command)
        return result
