from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteAdminCommand:
    id: str
    triggered_by_id: str | None = None
