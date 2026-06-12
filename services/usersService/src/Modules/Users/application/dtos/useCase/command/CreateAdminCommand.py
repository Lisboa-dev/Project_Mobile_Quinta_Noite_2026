from dataclasses import dataclass


@dataclass(frozen=True)
class CreateAdminCommand:
    userName: str
    email: str
    name: str
    password: str
    triggered_by_id: str | None = None
