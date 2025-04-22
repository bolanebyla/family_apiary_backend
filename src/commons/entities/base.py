import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from commons.datetime_utils import now_tz

EntityId = NewType('EntityId', uuid.UUID)


def create_entity_id() -> EntityId:
    """
    Создаёт идентификатор сущности
    """
    return EntityId(uuid.uuid4())


@dataclass
class BaseEntity:
    """
    Базовый класс сущности
    """

    id: EntityId
    created_at: datetime
    updated_at: datetime

    def set_updated_at(self) -> None:
        """
        Устанавливает время обновления как текущее время
        """
        self.updated_at = now_tz()
