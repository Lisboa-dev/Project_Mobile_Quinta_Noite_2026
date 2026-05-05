import re
import bcrypt  # pip install bcrypt

class Password:
    def __init__(self, valor: str, hashed: bool = False):
        """
        valor: senha em texto puro ou já hash
        hashed: se True, assume que 'valor' já é hash e não precisa validar
        """
        if hashed:
            self._hash = valor
        else:
            valor = valor.strip()
            if len(valor) < 8:
                raise ValueError("Senha deve ter pelo menos 8 caracteres")
            if not re.search(r"[A-Z]", valor):
                raise ValueError("Senha deve conter ao menos uma letra maiúscula")
            if not re.search(r"[a-z]", valor):
                raise ValueError("Senha deve conter ao menos uma letra minúscula")
            if not re.search(r"[0-9]", valor):
                raise ValueError("Senha deve conter ao menos um número")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", valor):
                raise ValueError("Senha deve conter ao menos um caractere especial")

            self._hash = self._hash_password(valor)

    @staticmethod
    def _hash_password(valor: str) -> str:
        return bcrypt.hashpw(valor.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, valor: str) -> bool:
        """Verifica se o valor bate com o hash"""
        return bcrypt.checkpw(valor.encode("utf-8"), self._hash.encode("utf-8"))

    @property
    def hash(self) -> str:
        """Retorna o hash da senha para salvar no banco"""
        return self._hash

    def __str__(self):
        return "***"  # nunca mostra a senha real

    def __repr__(self):
        return f"Password('***')"