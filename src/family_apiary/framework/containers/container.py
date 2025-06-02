from dishka import AsyncContainer, make_async_container

from family_apiary.framework.api.settings import (
    ApiPrometheusMetricsSettings,
    ApiSettings,
)
from family_apiary.framework.database.settings import DBSettings
from family_apiary.products.infrastructure.tg_chat_bot import TgChatBotSettings

from .providers import (
    CommandHandlersProvider,
    DBProvider,
    DBRepositoriesProvider,
    MapperProvider,
    MediatorProvider,
    OperationsProvider,
    TgChatBotProvider,
)


def create_api_container(
    api_settings: ApiSettings,
    api_prometheus_metrics_settings: ApiPrometheusMetricsSettings,
    tg_chat_bot_settings: TgChatBotSettings,
    db_settings: DBSettings,
) -> AsyncContainer:
    container = make_async_container(
        TgChatBotProvider(),
        CommandHandlersProvider(),
        MediatorProvider(),
        OperationsProvider(),
        DBRepositoriesProvider(),
        MapperProvider(),
        DBProvider(),
        context={
            ApiSettings: api_settings,
            ApiPrometheusMetricsSettings: api_prometheus_metrics_settings,
            TgChatBotSettings: tg_chat_bot_settings,
            DBSettings: db_settings,
        },
    )
    return container
