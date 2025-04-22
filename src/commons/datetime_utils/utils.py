from datetime import UTC, datetime


# TODO: сделать свой тип для даты с обязательным часовым поясом
def now_tz() -> datetime:
    """
    Получение текущего времени с часовым поясом
    """
    return datetime.now(UTC)
