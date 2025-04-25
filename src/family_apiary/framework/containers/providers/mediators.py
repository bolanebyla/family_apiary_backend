from dishka import Provider, Scope, provide

from commons.cqrs.base import CommandMediator, QueryMediator
from commons.cqrs.impl import CommandMediatorImpl, QueryMediatorImpl


class MediatorProvider(Provider):
    scope = Scope.APP

    query_mediator = provide(QueryMediatorImpl, provides=QueryMediator)
    command_mediator = provide(CommandMediatorImpl, provides=CommandMediator)
