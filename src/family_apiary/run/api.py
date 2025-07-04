import logging

import uvicorn

from family_apiary.framework import log
from family_apiary.framework.api.app import create_app
from family_apiary.framework.api.settings import (
    ApiPrometheusMetricsSettings,
    ApiSettings,
)
from family_apiary.framework.containers import create_api_container
from family_apiary.framework.database.settings import DBSettings
from family_apiary.products.infrastructure.tg_chat_bot import TgChatBotSettings

api_settings = ApiSettings()
api_prometheus_metrics_settings = ApiPrometheusMetricsSettings()
tg_chat_bot_settings = TgChatBotSettings()
db_settings = DBSettings()

log_config = log.create_config(
    # db_settings.LOGGING_CONFIG,
    api_settings.LOGGING_CONFIG,
)
log.configure(
    # db_settings.LOGGING_CONFIG,
    api_settings.LOGGING_CONFIG,
)

api_container = create_api_container(
    api_settings=api_settings,
    api_prometheus_metrics_settings=api_prometheus_metrics_settings,
    tg_chat_bot_settings=tg_chat_bot_settings,
    db_settings=db_settings,
)

app = create_app(
    api_settings=api_settings,
    container=api_container,
    api_prometheus_metrics_settings=api_prometheus_metrics_settings,
)

if __name__ == '__main__':
    logger = logging.getLogger('UvicornDevServer')
    logger.warning('API is running in development mode')

    uvicorn.run(
        'family_apiary.run.api:app',
        host='localhost',
        log_level='debug',
        log_config=log_config,
    )
