from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class UserEvent:
    id: str
    userName: str | None = None
    name: str | None = None
    email: str | None = None
    cargo: str | None = None
    triggered_by_id: str | None = None
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class UserCreatedEvent(UserEvent):
    pass


@dataclass(frozen=True)
class UserUpdatedEvent(UserEvent):
    changed_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class UserDeletedEvent(UserEvent):
    pass


@dataclass(frozen=True)
class UserProfileImageAddedEvent(UserEvent):
    profile_image_url: str | None = None
    profile_image_object: str | None = None
    previous_profile_image_object: str | None = None
