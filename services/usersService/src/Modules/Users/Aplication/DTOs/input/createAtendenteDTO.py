from typing import Protocol


class CreateAtendenteDTO(Protocol):
    name: str
    email: str
    password: str
    userName: str