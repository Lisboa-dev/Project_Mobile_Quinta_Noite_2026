from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateAdminCommand:
    id: int
    userName: str | None = None
    email: str | None = None
    name: str | None = None
    password: str | None = None
    triggered_by_id: str | None = None
