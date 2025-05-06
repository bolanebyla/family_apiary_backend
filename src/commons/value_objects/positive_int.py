from typing import SupportsIndex, SupportsInt

from typing_extensions import Buffer

from commons.app_errors import AppError


class PositiveIntValueMustBeGreaterThanZero(AppError):
    message_template = 'PositiveInt value must be greater than zero'


class PositiveInt(int):
    """Value object для положительного целого числа."""

    def __new__(
        cls, value: str | Buffer | SupportsInt | SupportsIndex
    ) -> 'PositiveInt':
        """Создает новый экземпляр PositiveInt.

        Args:
            value: Значение для преобразования в положительное целое число.

        Returns:
            PositiveInt: Новый экземпляр PositiveInt.

        Raises:
            PositiveIntValueMustBeGreaterThanZero: Если значение не является положительным числом.
        """
        instance = super().__new__(cls, value)
        if instance <= 0:
            raise PositiveIntValueMustBeGreaterThanZero()
        return instance
