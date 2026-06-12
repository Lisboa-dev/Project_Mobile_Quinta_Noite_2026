from dataclasses import dataclass, field




@dataclass(frozen=True)
class CreateClinicCommand:
    name: str
    triggered_by_id: str | None = None
    rules: list = field(default_factory=list)

@dataclass(frozen=True)
class UpdateClinicCommand:
    id: str
    triggered_by_id: str | None = None
    name: str | None = None
    rules: list | None = None

@dataclass(frozen=True)
class DeleteClinicCommand:
    id: str
    triggered_by_id: str | None = None
