from dataclasses import asdict, is_dataclass
from typing import Any


def command_to_context(command: Any) -> Any:
    model_dump = getattr(command, "model_dump", None)
    if callable(model_dump):
        return model_dump()

    to_dict = getattr(command, "dict", None)
    if callable(to_dict):
        return to_dict()

    if is_dataclass(command):
        return asdict(command)

    return str(command)
