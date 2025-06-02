import sys

from alembic.config import CommandLine, Config

from family_apiary.framework import log
from family_apiary.framework.database.settings import DBSettings
from family_apiary.products.infrastructure.database import (
    ProductsAlembicSettings,
)


class Settings:
    db = DBSettings()
    products_alembic = ProductsAlembicSettings()


class Logger:
    log.configure(Settings.db.LOGGING_CONFIG)


def make_config() -> Config:
    """
    Создаёт конфиг для логера
    """
    config = Config()
    config.set_main_option(
        'script_location', Settings.products_alembic.ALEMBIC_SCRIPT_LOCATION
    )
    config.set_main_option(
        'version_locations', Settings.products_alembic.ALEMBIC_VERSION_LOCATIONS
    )
    config.set_main_option('sqlalchemy.url', Settings.db.DB_URL)
    config.set_main_option(
        'file_template',
        Settings.products_alembic.ALEMBIC_MIGRATION_FILENAME_TEMPLATE,
    )
    config.set_main_option('timezone', 'UTC')

    return config


def run_cmd(*args: str) -> None:
    log.configure(Settings.db.LOGGING_CONFIG)
    cli = CommandLine()
    cli.run_cmd(make_config(), cli.parser.parse_args(args))


if __name__ == '__main__':
    run_cmd(*sys.argv[1:])
