import bcrypt

from commons.security.base import IPwdManager


class PwdManager(IPwdManager):
    """
    Класс для управления паролями
    """

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """
        Проверяет подлинность пароля. Сравнивает пароль с хэшом
        """
        password_byte_enc = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(
            password=password_byte_enc,
            hashed_password=hashed_password_bytes,
        )

    def get_password_hash(self, password: str) -> str:
        """
        Создаёт хэш из пароля
        """
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password_bytes = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        hashed_password = hashed_password_bytes.decode('utf-8')
        return hashed_password
