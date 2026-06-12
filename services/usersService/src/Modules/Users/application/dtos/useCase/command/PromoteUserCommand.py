from dataclasses import dataclass


@dataclass(frozen=True)
class PromoteUserCommand:
    id: str
    triggered_by_id: str | None = None
