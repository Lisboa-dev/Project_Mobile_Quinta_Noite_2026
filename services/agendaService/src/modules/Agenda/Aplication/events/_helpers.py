from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def enum_value(value: Any) -> Any:
    if value is None:
        return None
    return getattr(value, "value", str(value))


def id_list(items: list[Any] | None) -> list[str]:
    return [str(getattr(item, "id", item)) for item in (items or [])]


def rule_ids(items: list[Any] | None) -> list[str]:
    return id_list(items)
