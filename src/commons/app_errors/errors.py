import re

__camel_case_re = re.compile(r'(?<!^)(?=[A-Z])')


def camel_case_to_dash(text: str) -> str:
    """
    Переводит "СamelСase" в "dash"

    Пример: HelloWorldService -> hello_world_service
    """
    return __camel_case_re.sub('_', text).lower()


class AppError(Exception):
    code: str | None = None
    message_template: str | None = None

    def __init__(self, **kwargs: str):
        if 'message' in kwargs:
            self.message = kwargs['message']
        elif self.message_template:
            self.message = self.message_template.format(**kwargs)
        else:
            self.message = ''

        if self.code is None:
            self.code = camel_case_to_dash(self.__class__.__name__)

    def __str__(self) -> str:
        return self.message
