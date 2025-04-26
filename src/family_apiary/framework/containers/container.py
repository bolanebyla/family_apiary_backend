from dishka import make_async_container

from family_apiary.products.infrastructure.tg_chat_bot import TgChatBotSettings

from .providers import (
    CommandHandlersProvider,
    MediatorProvider,
    OperationsProvider,
    TgChatBotProvider,
)

tg_chat_bot_settings = TgChatBotSettings()

container = make_async_container(
    TgChatBotProvider(),
    CommandHandlersProvider(),
    MediatorProvider(),
    OperationsProvider(),
    context={
        TgChatBotSettings: tg_chat_bot_settings,
    },
)
