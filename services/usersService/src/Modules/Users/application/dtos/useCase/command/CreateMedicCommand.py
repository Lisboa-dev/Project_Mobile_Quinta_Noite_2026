from dataclasses import dataclass


@dataclass(frozen=True)
class CreateMedicCommand:
    userName: str
    email: str
    name: str
    password: str
    crm: str
    triggered_by_id: str | None = None
