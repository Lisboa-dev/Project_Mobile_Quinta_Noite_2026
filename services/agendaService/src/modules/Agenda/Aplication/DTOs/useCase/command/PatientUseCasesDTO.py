from dataclasses import dataclass




@dataclass(frozen=True)
class CreatePatientCommand:
    id: str
    name: str
    triggered_by_id: str | None = None

@dataclass(frozen=True)
class UpdatePatientCommand:
    id: str
    triggered_by_id: str | None = None
    name: str | None = None

@dataclass(frozen=True)
class DeletePatientCommand:
    id: str
    triggered_by_id: str | None = None
