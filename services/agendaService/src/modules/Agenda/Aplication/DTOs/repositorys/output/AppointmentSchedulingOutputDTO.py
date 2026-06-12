
from dataclasses import dataclass
from src.modules.agenda.domain.entities import Day, Doctor, Room
from src.modules.agenda.domain.entities.Appointment import Appointment
from src.modules.agenda.domain.entities.Patient import Patient
from src.modules.agenda.domain.valueObjects import Hour
from src.modules.agenda.domain.valueObjects.AppointmentType import AppointmentType
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime


    
@dataclass(frozen=True)
class AppointmentSchedulingOutputDTO:
    doctor: Doctor
    day: Day
    patient: Patient
    rooms: list[Room]
    room: list[Room]
    appointmentsToDoctor: list[Appointment]
    appointmentsToPatient: list[Appointment]
    type: AppointmentType
    time: Hour
    rangeTime: RangeTime
    appointments: list[Appointment]
