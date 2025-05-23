from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from commons.db.sqlalchemy import (
    AsyncReadOnlyTransactionContext,
    AsyncTransactionContext,
)
from family_apiary.framework.database.settings import DBSettings


def create_async_engine_from_settings(
    settings: DBSettings,
) -> AsyncEngine:
    return create_async_engine(
        url=settings.DB_URL,
        echo=settings.DB_ECHO,
    )


def create_db_read_only_transaction_context(
    db_engine: AsyncEngine,
) -> AsyncReadOnlyTransactionContext:
    return AsyncReadOnlyTransactionContext(
        bind=db_engine, expire_on_commit=False
    )


def create_db_transaction_context(
    db_engine: AsyncEngine,
) -> AsyncTransactionContext:
    return AsyncTransactionContext(bind=db_engine, expire_on_commit=False)
