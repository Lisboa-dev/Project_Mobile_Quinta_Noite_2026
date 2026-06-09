from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClientHealth:
    name: str
    ok: bool
    detail: str | None = None
    metadata: dict[str, Any] | None = None
