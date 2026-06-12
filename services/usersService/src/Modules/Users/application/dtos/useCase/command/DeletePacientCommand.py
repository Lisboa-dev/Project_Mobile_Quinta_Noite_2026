from dataclasses import dataclass


@dataclass(frozen=True)
class DeletePacientCommand:
    id: str
    triggered_by_id: str | None = None
