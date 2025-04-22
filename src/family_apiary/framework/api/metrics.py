import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from family_apiary.framework.api.settings import ApiPrometheusMetricsSettings


def configure_prometheus_metrics_endpoint(
    app: FastAPI,
    settings: ApiPrometheusMetricsSettings,
) -> None:
    """
    Конфигурирует эндпоинт для сбора метрик
    """
    # TODO: подумать над конфигурацией логов;
    #  сейчас логи конфигурируются после инициализации метрик
    logger = logging.getLogger('configure_metrics_endpoint')

    if settings.PROMETHEUS_METRICS_ENABLED:
        logger.info('Prometheus metrics enabled')
        Instrumentator().instrument(app=app).expose(
            app=app,
            endpoint=settings.PROMETHEUS_METRICS_ENDPOINT,
        )
    else:
        logger.info('Prometheus metrics disabled')
