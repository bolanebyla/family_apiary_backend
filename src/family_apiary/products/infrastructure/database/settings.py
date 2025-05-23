from pydantic_settings import BaseSettings


class ProductsAlembicSettings(BaseSettings):
    # Python путь к каталогу, где лежит запускатор alembic
    # (пример: <project_name>.composites:alembic)
    ALEMBIC_SCRIPT_LOCATION: str = (
        'family_apiary.products.infrastructure.database:alembic'
    )

    # Python путь к каталогу с миграциями
    ALEMBIC_VERSION_LOCATIONS: str = (
        'family_apiary.products.infrastructure.database:migrations'
    )

    ALEMBIC_MIGRATION_FILENAME_TEMPLATE: str = (
        '%%(year)d_'
        '%%(month).2d_'
        '%%(day).2d_'
        '%%(hour).2d_'
        '%%(minute).2d_'
        '%%(second).2d_'
        '%%(slug)s'
    )

    class Config:
        env_prefix = 'PRODUCTS_'
