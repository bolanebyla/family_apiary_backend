from typing import Any

from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    DB_URL: str
    DB_ECHO: bool = False

    LOGGING_LEVEL: str = 'INFO'

    @property
    def LOGGING_CONFIG(self) -> dict[str, Any]:
        config = {
            'loggers': {
                'alembic': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False,
                }
            }
        }

        if self.DB_ECHO:
            config['loggers']['sqlalchemy'] = {
                'handlers': ['default'],
                'level': self.LOGGING_LEVEL,
                'propagate': False,
            }

        return config
