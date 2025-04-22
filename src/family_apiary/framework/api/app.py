import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from commons.api.exception_handlers import app_error_handler
from commons.app_errors import AppError

# from .metrics import configure_prometheus_metrics_endpoint
from family_apiary.products.infrastructure.api_controllers import (
    products_router,
)

# from family_apiary.framework.api.settings import (
#     ApiPrometheusMetricsSettings,
#     ApiSettings,
# )


root_router = APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Выполняет действия перед запуском и после завершения основного приложения
    """
    logger = logging.getLogger('FastAPI lifespan')
    logger.info('Lifespan loading...')

    logger.info('Lifespan loaded')
    yield
    logger.info('Lifespan cleaning up...')

    logger.info('Lifespan cleaned up')


def create_app(
    # settings: ApiSettings,
    # api_prometheus_metrics_settings: ApiPrometheusMetricsSettings,
) -> FastAPI:
    """
    Создаёт инстанс fast api
    """
    app = FastAPI(
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
        debug=True,  # settings.API_DEBUG_MODE, TODO:!!!
    )
    app.include_router(root_router)
    api_router = APIRouter(prefix='/api')

    api_router.include_router(products_router)

    app.include_router(api_router)

    app.add_exception_handler(AppError, app_error_handler)

    # configure_prometheus_metrics_endpoint(
    #     app=app,
    #     settings=api_prometheus_metrics_settings,
    # )

    return app


@root_router.get('/', include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    """
    Редирект на страницу документации
    """
    return RedirectResponse(url='/docs')
