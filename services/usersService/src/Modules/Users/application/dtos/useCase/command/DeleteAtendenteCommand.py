from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteAtendenteCommand:
    id: int
    triggered_by_id: str | None = None
