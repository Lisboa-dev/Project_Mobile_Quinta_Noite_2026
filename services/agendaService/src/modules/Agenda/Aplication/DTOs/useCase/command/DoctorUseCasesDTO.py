from dataclasses import dataclass




@dataclass(frozen=True)
class CreateDoctorCommand:
    id_extern: str
    name: str
    triggered_by_id: str | None = None

@dataclass(frozen=True)
class UpdateDoctorCommand:
    id: str
    triggered_by_id: str | None = None
    name: str | None = None
    availability: bool | None = None
    rules: list | None = None

@dataclass(frozen=True)
class DeleteDoctorCommand:
    id: str
    triggered_by_id: str | None = None
