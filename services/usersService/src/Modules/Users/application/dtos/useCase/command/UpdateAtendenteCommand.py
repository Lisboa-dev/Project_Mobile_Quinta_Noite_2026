from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateAtendenteCommand:
    id: int
    userName: str | None = None
    email: str | None = None
    name: str | None = None
    password: str | None = None
    cpf: str | None = None
    triggered_by_id: str | None = None
