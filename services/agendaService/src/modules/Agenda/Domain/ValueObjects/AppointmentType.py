from dataclasses import dataclass


@dataclass(frozen=True)
class AppointmentType:
    name: str
    duration: int
    description: str
