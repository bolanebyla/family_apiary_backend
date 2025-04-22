from contextvars import ContextVar
from typing import Any

import msgspec
from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from commons.types import ContextBool

from .base import BaseCache, BaseCacheException, Key, KeyFieldType


class TransactionHasNotStarted(BaseCacheException):
    """
    Транзакция не начата - не вошли в контекстный менеджер
    """

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = (
                'The transaction has not started '
                'or has already been completed. '
                'The action must be performed inside the context manager.'
            )
        super().__init__(message)


class ReddisCache(BaseCache):
    """
    Асинхронный кэш на основе Raddis

    Контекстный менеджер.
    Запись в reddis происходит в блоке `__aexit__`
    """

    def __init__(self, client: Redis):
        self._client = client
        self._is_in_transaction = ContextBool(False)
        self._context_pipeline: ContextVar[Pipeline] = ContextVar(
            'context_pipeline'
        )

        self._context_current_values: ContextVar[Any] = ContextVar(
            'context_current_values'
        )

    def _get_pipeline_if_exists(self) -> Pipeline | None:
        return self._context_pipeline.get(None)

    def _get_current_value(self, key: bytes) -> bytes | None:
        current_values = self._context_current_values.get({})
        value: bytes | None = current_values.get(key, None)
        return value

    def _set_current_value(self, key: bytes, value: bytes) -> None:
        current_values = self._context_current_values.get({})
        current_values[key] = value
        self._context_current_values.set(current_values)

    @property
    def _current_pipeline(self) -> Pipeline:
        if not self._is_in_transaction:
            raise TransactionHasNotStarted()

        pipeline = self._get_pipeline_if_exists()
        if pipeline is None:
            pipeline = self._client.pipeline()
            self._context_pipeline.set(pipeline)

        return pipeline

    async def __aenter__(self) -> 'ReddisCache':
        self._is_in_transaction.set_true()
        return self

    async def __aexit__(self, *exc: Exception) -> bool | None:
        pipeline = self._get_pipeline_if_exists()
        if pipeline is None:
            return None

        if exc[0] is None:
            await pipeline.execute()
        else:
            await pipeline.reset()  # type: ignore

        self._is_in_transaction.set_false()
        return False

    async def set_value(
        self,
        key: Key[KeyFieldType],
        value: KeyFieldType,
        ttl: int | None = None,
    ) -> None:
        encoded_value = msgspec.json.encode(value)

        self._set_current_value(key=key.serialize(), value=encoded_value)
        if ttl is not None:
            await self._current_pipeline.setex(
                name=key.serialize(),
                value=encoded_value,
                time=ttl,
            )
        else:
            await self._current_pipeline.set(
                name=key.serialize(),
                value=encoded_value,
            )

    async def get_value(self, key: Key[KeyFieldType]) -> KeyFieldType | None:
        if not self._is_in_transaction:
            raise TransactionHasNotStarted()

        value = self._get_current_value(
            key=key.serialize(),
        )
        if value is None:
            print('_client', self._client)
            value = await self._client.get(name=key.serialize())

        if value is None:
            return None

        decoded_value: KeyFieldType | None = msgspec.json.decode(
            value,
            type=key.item_field_type,
        )
        return decoded_value
