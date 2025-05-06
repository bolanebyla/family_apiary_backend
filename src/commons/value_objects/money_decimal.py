from decimal import Context, Decimal
from typing import Any

from commons.app_errors import AppError


class MoneyValueCannotBeLessThanZero(AppError):
    message_template = 'Money value cannot be less than zero'


class MoneyDecimal(Decimal):
    """
    Класс для работы с денежными суммами, наследующийся от Decimal.
    Гарантирует, что значение не может быть отрицательным.
    """

    def __new__(
        cls, value: str | int | float | Decimal, context: Context | None = None
    ) -> 'MoneyDecimal':
        decimal_value = super().__new__(cls, value, context)

        if decimal_value < 0:
            raise MoneyValueCannotBeLessThanZero()

        return decimal_value

    def __add__(self, other: Any) -> 'MoneyDecimal':
        """Сложение с другим значением"""
        result = super().__add__(other)
        return MoneyDecimal(result)

    def __sub__(self, other: Any) -> 'MoneyDecimal':
        """Вычитание другого значения"""
        result = super().__sub__(other)
        return MoneyDecimal(result)

    def __mul__(self, other: Any) -> 'MoneyDecimal':
        """Умножение на число"""
        result = super().__mul__(other)
        return MoneyDecimal(result)

    def __truediv__(self, other: Any) -> 'MoneyDecimal':
        """Деление на число"""
        if other == 0:
            raise ValueError('Деление на ноль невозможно')
        result = super().__truediv__(other)
        return MoneyDecimal(result)

    @classmethod
    def from_int(cls, value: int) -> 'MoneyDecimal':
        """Создание из целого числа"""
        return cls(str(value))

    @classmethod
    def from_float(cls, value: float) -> 'MoneyDecimal':
        """Создание из числа с плавающей точкой"""
        return cls(str(value))

    @classmethod
    def zero(cls) -> 'MoneyDecimal':
        """Создание нулевой суммы"""
        return cls('0')
