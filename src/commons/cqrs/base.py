from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TRequest = TypeVar('TRequest')
TResult = TypeVar('TResult')


class _RequestHandler(ABC, Generic[TRequest, TResult]):
    """
    Базовый обработчик
    """

    @abstractmethod
    async def handle(self, request: TRequest) -> TResult:
        pass


class CommandHandler(_RequestHandler[TRequest, TResult], ABC):
    """
    Базовый обработчик команд
    """

    @abstractmethod
    async def handle(self, command: TRequest) -> TResult: ...


class QueryHandler(_RequestHandler[TRequest, TResult], ABC):
    """
    Базовый обработчик запросов
    """

    @abstractmethod
    async def handle(self, query: TRequest) -> TResult: ...


class QueryMediator(ABC):
    """
    Базовый медиатор запросов
    """

    @abstractmethod
    async def send(self, query: TRequest) -> TResult | None: ...


class CommandMediator(ABC):
    """
    Базовый медиатор команд
    """

    @abstractmethod
    async def send(self, command: TRequest) -> TResult | None: ...
