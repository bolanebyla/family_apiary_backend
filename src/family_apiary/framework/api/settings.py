from typing import Any

from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    LOGGING_LEVEL: str = 'INFO'
    API_DEBUG_MODE: bool = False

    @property
    def LOGGING_CONFIG(self) -> dict[str, Any]:
        config = {
            'loggers': {
                'uvicorn': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
                'uvicorn.access': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
                'uvicorn.error': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
                'uvicorn.asgi': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
                'gunicorn': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
                'gunicorn.access': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
                'gunicorn.error': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                },
            }
        }

        return config


class ApiPrometheusMetricsSettings(BaseSettings):
    PROMETHEUS_METRICS_ENABLED: bool = True
    PROMETHEUS_METRICS_ENDPOINT: str = '/metrics'
