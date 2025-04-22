from abc import ABC, abstractmethod
from typing import Generic, Iterable, Type, TypeVar

import msgspec

KeyFieldType = TypeVar('KeyFieldType', bound=object)

KEY_SEPARATOR = ':'
KEY_ITEM_IDS_SEPARATOR = ','


class BaseCacheException(Exception):
    """
    Базовое исключение для кеша
    """

    pass


class KeyTemplate(Generic[KeyFieldType]):
    """
    Шаблон ключа

    :param namespace: Контекст (модуль)
    :param item_name: Наименование сущности
    :param item_field_name: Наименование поля
    :param item_field_type: Тип поля
    """

    namespace: str
    item_name: str
    item_field_name: str
    item_field_type: Type[KeyFieldType]

    def __init__(
        self,
        namespace: str,
        item_name: str,
        item_field_name: str,
        item_field_type: Type[KeyFieldType],
    ):
        self.namespace = namespace
        self.item_name = item_name
        self.item_field_name = item_field_name
        self.item_field_type = item_field_type


class Key(KeyTemplate[KeyFieldType]):
    """
    Ключ

    :param namespace: Контекст (модуль)
    :param item_name: Наименование сущности
    :param item_field_name: Наименование поля
    :param item_field_type: Тип поля
    :param item_ids: Идентификаторы сущностей
    """

    item_ids: Iterable[str]

    def __init__(
        self,
        namespace: str,
        item_name: str,
        item_field_name: str,
        item_field_type: Type[KeyFieldType],
        item_ids: Iterable[str] | None = None,
    ):
        super().__init__(namespace, item_name, item_field_name, item_field_type)
        if item_ids:
            self.item_ids = item_ids
        else:
            self.item_ids = []

    def serialize(self) -> bytes:
        return msgspec.json.encode(str(self))

    def __str__(self) -> str:
        item_ids_str = f'{KEY_ITEM_IDS_SEPARATOR}'.join(self.item_ids)

        return (
            f'{self.namespace}'
            f'{KEY_SEPARATOR}{self.item_name}'
            f'{KEY_SEPARATOR}{item_ids_str}'
            f'{KEY_SEPARATOR}{self.item_field_name}'
        )

    @staticmethod
    def create_for_items(
        key_template: KeyTemplate[KeyFieldType],
        *item_ids: str,
    ) -> 'Key[KeyFieldType]':
        """
        Создаёт ключ по шаблону
        """
        return Key(
            namespace=key_template.namespace,
            item_name=key_template.item_name,
            item_field_name=key_template.item_field_name,
            item_field_type=key_template.item_field_type,
            item_ids=item_ids,
        )


# TODO: перенести логику серилизации в базовый класс
class BaseCache(ABC):
    """
    Базовый класс кеша
    """

    @abstractmethod
    async def set_value(
        self,
        key: Key[KeyFieldType],
        value: KeyFieldType,
        ttl: int | None = None,
    ) -> None:
        """
        Установить значение по ключу

        :param key: ключ
        :param value: значение
        :param ttl: время хранения в секундах
        """
        ...

    @abstractmethod
    async def get_value(self, key: Key[KeyFieldType]) -> KeyFieldType | None:
        """
        Получить значение по ключу

        :param key: ключ
        """
        ...
