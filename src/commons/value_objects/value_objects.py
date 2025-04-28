import re

from commons.app_errors import AppError


class PhoneNumberInvalid(AppError):
    message_template = 'Phone number invalid'


class PhoneNumber(str):
    phone_number_pattern_regex = r'^(\+)[1-9][0-9\-\(\)\.]{9,18}$'

    def __new__(cls, value: str) -> 'PhoneNumber':
        obj = str.__new__(cls, value)
        cls.validate(obj)
        return obj

    @staticmethod
    def validate(value: str) -> None:
        """
        Проверяет соответствие строки паттерну номера телефона

        :raises PhoneNumberInvalid: если строка не соответствует паттерну номера телефона
        """
        regex = r'^(\+)[1-9][0-9\-\(\)\.]{9,18}$'
        if value and not re.search(regex, value, re.I):
            raise PhoneNumberInvalid()
