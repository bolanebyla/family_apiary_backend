from dishka import Provider, Scope, provide

from commons.db.sqlalchemy import (
    AsyncReadOnlyTransactionContext,
    AsyncTransactionContext,
)
from commons.operations.operations import AsyncOperation


class OperationsProvider(Provider):
    scope = Scope.APP

    @provide
    def create_operations(
        self,
        db_transaction_context: AsyncTransactionContext,
        db_read_only_transaction_context: AsyncReadOnlyTransactionContext,
    ) -> AsyncOperation:
        operation = AsyncOperation(
            context_managers=[
                db_read_only_transaction_context,
                db_transaction_context,
            ]
        )
        return operation
