from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from commons.db.sqlalchemy import (
    AsyncReadOnlyTransactionContext,
    AsyncTransactionContext,
)
from family_apiary.framework.database.engine import (
    create_async_engine_from_settings,
)
from family_apiary.framework.database.settings import DBSettings


class DBProvider(Provider):
    scope = Scope.APP

    db_settings = from_context(provides=DBSettings, scope=Scope.APP)

    @provide
    def create_db_engine(
        self,
        db_settings: DBSettings,
    ) -> AsyncEngine:
        return create_async_engine_from_settings(settings=db_settings)

    db_transaction_context = provide(
        AsyncTransactionContext,
    )
    db_read_only_transaction_context = provide(
        AsyncReadOnlyTransactionContext,
    )
