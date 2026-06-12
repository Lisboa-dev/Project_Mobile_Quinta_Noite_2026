from ..exceptions.DomainExceptions import InvalidUsernameException


class UserName:
    def __init__(self, value: str):
        value = (value or "").strip()
        if len(value) < 3:
            raise InvalidUsernameException("userName deve ter pelo menos 3 caracteres")
        self.value = value

    @property
    def valor(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"UserName('{self.value}')"
