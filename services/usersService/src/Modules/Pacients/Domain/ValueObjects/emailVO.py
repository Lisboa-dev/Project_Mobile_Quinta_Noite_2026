import re

class Email:
    EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    def __init__(self, valor: str):
        valor = valor.strip()
        if not re.match(self.EMAIL_REGEX, valor):
            raise ValueError(f"Email inválido: {valor}")
        self.valor = valor

    def __str__(self):
        return self.valor

    def __repr__(self):
        return f"Email('{self.valor}')"