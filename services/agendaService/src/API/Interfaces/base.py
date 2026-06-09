import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


TIME_PATTERN = re.compile(r"^\d{2}:\d{2}$")


class ApiInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    triggered_by_id: str | None = None

    @field_validator("triggered_by_id")
    @classmethod
    def validate_triggered_by_id(cls, value: str | None) -> str | None:
        return optional_non_empty(value, "triggered_by_id")


def required_non_empty(value: Any, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required")
    return str(value).strip()


def optional_non_empty(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        raise ValueError(f"{field_name} cannot be empty")
    return value


def validate_time_text(value: Any, field_name: str) -> str:
    value = required_non_empty(value, field_name)
    if not TIME_PATTERN.match(value):
        raise ValueError(f"{field_name} must use HH:MM format")
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid time") from exc
    return value


def validate_iso_date_text(value: Any, field_name: str) -> str:
    value = required_non_empty(value, field_name)
    try:
        datetime.strptime(value.split("T", 1)[0], "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc
    return value


def validate_range_time(value: Any, field_name: str) -> Any:
    if isinstance(value, dict):
        start = value.get("start_time") or value.get("start")
        end = value.get("end_time") or value.get("end")
        validate_time_text(start, f"{field_name}.start_time")
        validate_time_text(end, f"{field_name}.end_time")
        return value
    text = required_non_empty(value, field_name)
    if "-" not in text:
        raise ValueError(f"{field_name} must use 'HH:MM-HH:MM' or range object")
    start, end = text.split("-", 1)
    validate_time_text(start.strip(), f"{field_name}.start_time")
    validate_time_text(end.strip(), f"{field_name}.end_time")
    return value


def validate_weekday(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 0 or value > 6:
        raise ValueError("weekday must be between 0 and 6")
    return value
