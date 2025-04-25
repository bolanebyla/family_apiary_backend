from dishka import Provider, Scope, provide

from commons.operations.operations import AsyncOperation


class OperationsProvider(Provider):
    scope = Scope.APP

    @provide
    def create_operations(self) -> AsyncOperation:
        operation = AsyncOperation()
        return operation
