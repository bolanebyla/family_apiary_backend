from dishka import make_async_container

from .providers import (
    CommandHandlersProvider,
    MediatorProvider,
    OperationsProvider,
    SettingsProvider,
    TgChatBotProvider,
)

container = make_async_container(
    SettingsProvider(),
    TgChatBotProvider(),
    CommandHandlersProvider(),
    MediatorProvider(),
    OperationsProvider(),
)
