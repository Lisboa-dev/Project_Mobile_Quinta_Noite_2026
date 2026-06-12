from dataclasses import dataclass


@dataclass(frozen=True)
class CreatePacientCommand:
    userName: str
    email: str
    name: str
    password: str
    cpf: str
    triggered_by_id: str | None = None
