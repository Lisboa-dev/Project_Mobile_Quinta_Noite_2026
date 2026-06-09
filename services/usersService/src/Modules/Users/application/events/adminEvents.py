from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class AdminCreatedEvent:
    id: str
    userName: str
    name: str
    email: str
    cargo: str = "ADMIN"
    cpf: str | None = None
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class AdminDeletedEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    cargo: str = "ADMIN"
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class AdminUpdatedEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    cargo: str = "ADMIN"
    changed_fields: tuple[str, ...] = ()
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class UserPromotedEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    previous_cargo: str | None = None
    cargo: str = "ADMIN"
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class UserDepreciatEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    previous_cargo: str | None = None
    cargo: str = "ATENDENTE"
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)
