import asyncio
from typing import Literal, MutableMapping

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from family_apiary.products.infrastructure.database import tables
from family_apiary.products.infrastructure.database.meta import metadata

app_tables = tables

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        include_schemas=True,
        version_table_schema=target_metadata.schema,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def include_only_current_schema(
    name: str | None,
    type_: Literal[
        'schema',
        'table',
        'column',
        'index',
        'unique_constraint',
        'foreign_key_constraint',
    ],
    parent_names: MutableMapping[
        Literal[
            'schema_name',
            'table_name',
            'schema_qualified_table_name',
        ],
        str | None,
    ],
) -> bool:
    """
    Проверят, что схема является схемой из metadata.
    Для SQLite пропускает проверку схемы.
    """
    # Для SQLite пропускаем проверку схемы
    if context.get_bind().dialect.name == 'sqlite':
        return True

    if type_ == 'schema':
        return name in [target_metadata.schema]
    else:
        return True


def get_table_name(name: str, schema: str | None) -> str:
    """
    Для SQLite добавляет имя схемы к имени таблицы, чтобы избежать конфликтов имен.
    Для других БД возвращает оригинальное имя таблицы.
    """
    if context.get_bind().dialect.name == 'sqlite' and schema:
        return f'{schema}_{name}'
    return name


def include_object(object, name, type_, reflected, compare_to):
    """
    Фильтрует объекты для SQLite, убирая схему из имен таблиц
    """
    if context.get_bind().dialect.name == 'sqlite':
        if type_ == 'table':
            # Убираем схему из имени таблицы
            object.schema = None
    return True


def do_run_migrations(connection: Connection) -> None:  # noqa: D103
    # Для SQLite убираем схему из конфигурации
    if connection.dialect.name == 'sqlite':
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_only_current_schema,
            include_schemas=False,  # Отключаем поддержку схем для SQLite
            include_object=include_object,  # Добавляем фильтр объектов
        )
    else:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
            include_name=include_only_current_schema,
            include_schemas=True,
        )

    with context.begin_transaction():
        # Создаем схему перед созданием таблиц
        if connection.dialect.name != 'sqlite':
            context.execute(
                f'CREATE SCHEMA IF NOT EXISTS {target_metadata.schema}'
            )
            # Устанавливаем схему по умолчанию для текущей сессии
            context.execute(f'SET search_path TO {target_metadata.schema}')
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
