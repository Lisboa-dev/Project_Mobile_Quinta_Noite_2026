from dataclasses import dataclass




@dataclass(frozen=True)
class CreateRoomCommand:
    name: str
    triggered_by_id: str | None = None

@dataclass(frozen=True)
class UpdateRoomCommand:
    id: str
    triggered_by_id: str | None = None
    name: str | None = None
    disponibility: bool | None = None
    rules: list | None = None

@dataclass(frozen=True)
class DeleteRoomCommand:
    id: str
    triggered_by_id: str | None = None
