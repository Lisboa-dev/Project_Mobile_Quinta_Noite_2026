from datetime import datetime, timezone
from inspect import isawaitable
from typing import Any


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def maybe_await(value):
    if isawaitable(value):
        return await value
    return value


def read_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, tuple) and len(value) == 1:
        value = value[0]
    if not isinstance(value, tuple) and hasattr(value, "valor"):
        return value.valor
    if not isinstance(value, tuple) and hasattr(value, "value"):
        nested = value.value
        return nested.value if hasattr(nested, "value") else nested
    if not isinstance(value, tuple) and hasattr(value, "id"):
        return value.id
    return value


def user_event_payload(user: Any, triggered_by_id: str | None = None, **extra) -> dict:
    payload = {
        "id": str(read_value(getattr(user, "id", None))),
        "userName": read_value(getattr(user, "userName", None)),
        "name": read_value(getattr(user, "name", None)),
        "email": read_value(getattr(user, "email", None)),
        "cargo": read_value(getattr(user, "cargo", None)),
        "triggered_by_id": triggered_by_id,
        "occurred_at": now_utc(),
        **extra,
    }
    profile_image_url = getattr(user, "profile_image_url", None)
    profile_image_object = getattr(user, "profile_image_object", None)
    if profile_image_url is not None:
        payload["profile_image_url"] = profile_image_url
    if profile_image_object is not None:
        payload["profile_image_object"] = profile_image_object
    return payload
