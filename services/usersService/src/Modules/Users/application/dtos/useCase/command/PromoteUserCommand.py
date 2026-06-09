from dataclasses import dataclass


@dataclass(frozen=True)
class PromoteUserCommand:
    id: int
    triggered_by_id: str | None = None
