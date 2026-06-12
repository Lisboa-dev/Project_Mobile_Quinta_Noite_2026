from ..exceptions.DomainExceptions import InvalidNameException


class Nome:
    def __init__(self, value: str):
        value = (value or "").strip()
        if len(value) < 2:
            raise InvalidNameException("nome deve ter pelo menos 2 caracteres")
        self.value = value

    @property
    def valor(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Nome('{self.value}')"
