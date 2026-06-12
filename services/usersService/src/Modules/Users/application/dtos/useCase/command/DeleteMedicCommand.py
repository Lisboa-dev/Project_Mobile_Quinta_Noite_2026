from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteMedicCommand:
    id: str
    triggered_by_id: str | None = None
