from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteAdminCommand:
    id: int
    triggered_by_id: str | None = None
