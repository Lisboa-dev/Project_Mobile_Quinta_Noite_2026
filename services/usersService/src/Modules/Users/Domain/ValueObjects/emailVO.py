import re

from ..exceptions.DomainExceptions import InvalidEmailException


class Email:
    EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    def __init__(self, value: str):
        value = (value or "").strip().lower()
        if not re.match(self.EMAIL_REGEX, value):
            raise InvalidEmailException(value)
        self.value = value

    @property
    def valor(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Email('{self.value}')"
