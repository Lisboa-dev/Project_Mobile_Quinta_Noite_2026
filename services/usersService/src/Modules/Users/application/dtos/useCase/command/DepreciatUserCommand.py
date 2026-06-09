from dataclasses import dataclass


@dataclass(frozen=True)
class DepreciatUserCommand:
    id: int
    triggered_by_id: str | None = None
