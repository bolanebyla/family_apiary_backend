from dishka import Provider, Scope, provide

from family_apiary.products.infrastructure.tg_chat_bot import TgChatBotSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def create_tg_chat_bot_settings(self) -> TgChatBotSettings:
        return TgChatBotSettings()
