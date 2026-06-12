from dataclasses import dataclass


@dataclass(frozen=True)
class AppointmentSchedulingInputDTO:
    patient: str
    doctor: str
    type: str
    time: str
    date: str
    weekday: str
    room: str | None = None
