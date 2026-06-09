from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MedicCreatedEvent:
    id: str
    userName: str
    name: str
    email: str
    cargo: str = "MEDICO"
    crm: str | None = None
    profile_image_url: str | None = None
    profile_image_object: str | None = None
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class MedicDeletedEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    cargo: str = "MEDICO"
    crm: str | None = None
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class MedicUpdatedEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    cargo: str = "MEDICO"
    crm: str | None = None
    changed_fields: tuple[str, ...] = ()
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class MedicImageAddedEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    cargo: str = "MEDICO"
    image_url: str | None = None
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)
