from dishka import make_async_container

from .providers import SettingsProvider, TgChatBotProvider

container = make_async_container(
    SettingsProvider(),
    TgChatBotProvider(),
)
