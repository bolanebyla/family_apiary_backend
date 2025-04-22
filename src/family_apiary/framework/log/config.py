import logging.config
from typing import Any

from .settings import LoggingSettings


def create_config(*configs: dict[str, Any]) -> dict[str, Any]:
    """
    Создаёт конфиг логера
    """
    result_config = LoggingSettings().LOGGING_CONFIG

    for config in configs:
        result_config['formatters'].update(config.get('formatters', {}))
        result_config['handlers'].update(config.get('handlers', {}))
        result_config['loggers'].update(config.get('loggers', {}))

    return result_config


def configure(*configs: dict[str, Any]) -> None:
    """
    Применяет конфиг к логеру
    """
    result_config = create_config(*configs)

    logging.config.dictConfig(result_config)
