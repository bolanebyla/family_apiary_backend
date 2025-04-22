from fastapi import Request
from starlette.responses import JSONResponse

from commons.app_errors import AppError


def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Создаёт обработчик ошибок слоя приложения
    """
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message,
            'code': exc.code,
        },
    )
