from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteAtendenteCommand:
    id: str
    triggered_by_id: str | None = None
