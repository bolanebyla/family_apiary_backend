from contextvars import ContextVar
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class BaseTransactionContextException(Exception):
    """
    Базовый класс контекстного менеджера транзакций
    """

    pass


class TransactionHasNotStartedError(BaseTransactionContextException):
    """
    Транзакция не начата - не вошли в контекстный менеджер
    """

    pass


class AsyncReadOnlyTransactionContext:
    """
    Контекст БД только для чтения
    """

    def __init__(self, **kwargs: Any):
        self.create_session = async_sessionmaker(**kwargs)

        self._context_sessions: ContextVar[AsyncSession] = ContextVar(
            'context_sessions'
        )

        self._context_is_in_transaction: ContextVar[bool] = ContextVar(
            'context_is_in_transaction'
        )

    def _get_session_if_exists(self) -> AsyncSession | None:
        return self._context_sessions.get(None)

    @property
    def current_session(self) -> AsyncSession:
        if not self._context_is_in_transaction.get(False):
            raise TransactionHasNotStartedError(
                'The transaction has not started or has already been completed.'
                'The action must be performed inside the context manager.'
            )
        session = self._get_session_if_exists()
        if session is None:
            session = self.create_session()
            self._context_sessions.set(session)
            self._context_is_in_transaction.set(True)
        return session

    async def __aenter__(self) -> 'AsyncReadOnlyTransactionContext':
        self._context_is_in_transaction.set(True)
        return self

    async def __aexit__(self, *exc: Exception) -> bool | None:
        self._context_is_in_transaction.set(False)
        session = self._get_session_if_exists()
        if session is None:
            return None

        await session.rollback()
        await session.close()
        return False


class AsyncTransactionContext(AsyncReadOnlyTransactionContext):
    """
    Контекст БД
    """

    async def __aexit__(self, *exc: Exception) -> bool | None:
        self._context_is_in_transaction.set(False)
        session = self._get_session_if_exists()
        if session is None:
            return None

        if exc[0] is None:
            await session.commit()
        else:
            await session.rollback()

        await session.close()
        return False


class BaseReadOnlyRepository:
    """
    Базовый класс репозитория только для чтения
    """

    def __init__(self, transaction_context: AsyncReadOnlyTransactionContext):
        self._transaction_context = transaction_context

    @property
    def session(self) -> AsyncSession:
        return self._transaction_context.current_session


class BaseRepository(BaseReadOnlyRepository):
    """
    Базовый класс репозитория
    """

    def __init__(self, transaction_context: AsyncTransactionContext):
        super().__init__(transaction_context)
