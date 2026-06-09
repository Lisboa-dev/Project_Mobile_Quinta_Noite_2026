from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteMedicCommand:
    id: int
    triggered_by_id: str | None = None
