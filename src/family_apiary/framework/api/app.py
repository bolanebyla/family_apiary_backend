import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from commons.api.exception_handlers import app_error_handler
from commons.app_errors import AppError
from commons.cqrs.base import CommandMediator, QueryMediator
from commons.cqrs.impl import CommandMediatorImpl, QueryMediatorImpl
from family_apiary.framework.api.metrics import (
    configure_prometheus_metrics_endpoint,
)
from family_apiary.framework.api.settings import (
    ApiPrometheusMetricsSettings,
    ApiSettings,
)
from family_apiary.products.infrastructure.api_controllers import (
    products_router,
)

root_router = APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Выполняет действия перед запуском и после завершения основного приложения
    """
    logger = logging.getLogger('FastAPI lifespan')
    logger.info('Lifespan loading...')

    # находим и регистрируем все обработчики запросов
    query_mediator: QueryMediatorImpl = await app.state.dishka_container.get(
        QueryMediator
    )
    query_mediator.resolve_handlers()

    # находим и регистрируем все обработчики команд
    command_mediator: CommandMediatorImpl = (
        await app.state.dishka_container.get(CommandMediator)
    )
    command_mediator.resolve_handlers()

    logger.info('Lifespan loaded')
    yield
    logger.info('Lifespan cleaning up...')
    await app.state.dishka_container.close()
    logger.info('Lifespan cleaned up')


def create_app(
    api_settings: ApiSettings,
    container: AsyncContainer,
    api_prometheus_metrics_settings: ApiPrometheusMetricsSettings,
) -> FastAPI:
    """
    Создаёт инстанс fast api
    """
    app = FastAPI(
        title='Family apiary',
        lifespan=lifespan,
        middleware=[
            # TODO: вынести CORS в настройки
            Middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            )
        ],
        debug=api_settings.API_DEBUG_MODE,
    )

    app.include_router(root_router)
    api_router = APIRouter(prefix='/api')

    api_router.include_router(products_router)

    app.include_router(api_router)

    app.add_exception_handler(AppError, app_error_handler)

    configure_prometheus_metrics_endpoint(
        app=app,
        settings=api_prometheus_metrics_settings,
    )

    setup_dishka(container=container, app=app)

    return app


@root_router.get('/', include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    """
    Редирект на страницу документации
    """
    return RedirectResponse(url='/docs')
