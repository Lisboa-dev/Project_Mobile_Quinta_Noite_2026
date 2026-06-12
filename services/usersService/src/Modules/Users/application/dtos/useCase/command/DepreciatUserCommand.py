from dataclasses import dataclass


@dataclass(frozen=True)
class DepreciatUserCommand:
    id: str
    triggered_by_id: str | None = None
