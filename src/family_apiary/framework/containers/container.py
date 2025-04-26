from dishka import make_async_container

from family_apiary.framework.api.settings import (
    ApiPrometheusMetricsSettings,
    ApiSettings,
)
from family_apiary.products.infrastructure.tg_chat_bot import TgChatBotSettings

from .providers import (
    CommandHandlersProvider,
    MediatorProvider,
    OperationsProvider,
    TgChatBotProvider,
)

api_settings = ApiSettings()
api_prometheus_metrics_settings = ApiPrometheusMetricsSettings()
tg_chat_bot_settings = TgChatBotSettings()

container = make_async_container(
    TgChatBotProvider(),
    CommandHandlersProvider(),
    MediatorProvider(),
    OperationsProvider(),
    context={
        ApiSettings: api_settings,
        ApiPrometheusMetricsSettings: api_prometheus_metrics_settings,
        TgChatBotSettings: tg_chat_bot_settings,
    },
)
