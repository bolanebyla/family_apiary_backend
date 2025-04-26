import logging

import uvicorn

from family_apiary.framework import log
from family_apiary.framework.api.app import create_app
from family_apiary.framework.containers import (
    api_prometheus_metrics_settings,
    api_settings,
)

app = create_app(
    api_settings=api_settings,
    api_prometheus_metrics_settings=api_prometheus_metrics_settings,
)

if __name__ == '__main__':
    # db_settings = container.resolve(DBSettings)
    #
    log_config = log.create_config(
        # db_settings.LOGGING_CONFIG,
        api_settings.LOGGING_CONFIG,
    )
    log.configure(
        # db_settings.LOGGING_CONFIG,
        api_settings.LOGGING_CONFIG,
    )

    logger = logging.getLogger('UvicornDevServer')
    logger.warning('API is running in development mode')

    uvicorn.run(
        'family_apiary.run.api:app',
        host='localhost',
        log_level='debug',
        log_config=log_config,
    )
