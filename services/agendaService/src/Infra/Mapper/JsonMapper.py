from enum import Enum
from datetime import date, datetime, time


def to_primitive(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, list):
        return [to_primitive(item) for item in value]
    if isinstance(value, tuple):
        return [to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {key: to_primitive(item) for key, item in value.items()}
    if hasattr(value, "model_dump"):
        return to_primitive(value.model_dump())
    if hasattr(value, "dict"):
        return to_primitive(value.dict())
    if hasattr(value, "__dict__"):
        data = {}
        for key, item in value.__dict__.items():
            clean_key = key[1:] if key.startswith("_") else key
            data[clean_key] = to_primitive(item)
        return data
    return str(value)
