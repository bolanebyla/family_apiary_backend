import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette import status

from commons.api.auth import JwtManager
from commons.cqrs.impl import QueryMediator
from commons.entities.base import EntityId
from plannery.framework.containers import container, get_query_mediator
from plannery.users.application.use_cases.query import (
    IsUserAuthSessionCancelledQuery,
    IsUserAuthSessionCancelledResult,
)


class CurrentClient(BaseModel):
    """
    Текущий клиент
    """

    user_id: EntityId
    auth_session_id: EntityId


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/users/auth/basic/login_by_password',
)


async def get_current_client(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    jwt_manager: Annotated[
        JwtManager, Depends(lambda: container.resolve(JwtManager))
    ],
    query_mediator: Annotated[QueryMediator, Depends(get_query_mediator)],
) -> CurrentClient:
    """
    Получает текущего клиента
    """
    token_claims = jwt_manager.verify_access_token(token=access_token)
    current_client = CurrentClient(
        user_id=EntityId(uuid.UUID(token_claims.sub)),
        auth_session_id=EntityId(uuid.UUID(token_claims.jti)),
    )

    query = IsUserAuthSessionCancelledQuery(
        auth_session_id=current_client.auth_session_id,
    )
    is_auth_session_cancelled_result: IsUserAuthSessionCancelledResult = (
        await query_mediator.send(query)
    )

    if is_auth_session_cancelled_result.is_cancelled:
        # TODO: вынести ошибку в константы
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return current_client
