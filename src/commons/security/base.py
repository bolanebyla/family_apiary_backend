from abc import ABC, abstractmethod

from plannery.users.application.entities import PasswordHash


class IPwdManager(ABC):
    """
    Класс для управления паролями
    """

    @abstractmethod
    def verify_password(
        self,
        plain_password: str,
        hashed_password: PasswordHash,
    ) -> bool:
        """
        Проверяет подлинность пароля. Сравнивает пароль с хэшом
        """
        ...

    @abstractmethod
    def get_password_hash(self, password: str) -> PasswordHash:
        """
        Создаёт хэш из пароля
        """
        ...
