from src.modules.agenda.domain.entities.Day import Day
from src.modules.agenda.domain.entities.Doctor import Doctor
from src.modules.agenda.domain.entities.Patient import Patient
from src.modules.agenda.domain.entities.Room import Room
from src.modules.agenda.domain.valueObjects import Date, Hour, RangeTime
from src.modules.agenda.domain.valueObjects.EnumAppointment import AppointmentStatus
from src.modules.agenda.domain.valueObjects.AppointmentType import  AppointmentType
from src.modules.agenda.domain.valueObjects.Id import ID




class Appointment:
   

    def __init__(
        self,
        rangeTime: RangeTime,
        patient: str,
        doctor: str,
        room: str,
        type: AppointmentType,
        time: Hour,
        status: AppointmentStatus,
        date: str,
        id: ID | None = None
    ) -> None:
        self._patient_id = patient
        self._doctor_id = doctor
        self._room_id = room
        self._type = type
        self._time = time
        self._status = status
        self._id = id or ID()
        self._rangeTime = rangeTime
        self._date = date
        
      
    
    @staticmethod
    def create(
        patient: Patient,
        doctor: Doctor,
        rooms: list[Room],
        day: Day,
        time: Hour,
        type: AppointmentType,
    ):
        
        raw_time = str(time)
        rangeTime = RangeTime.generate(raw_time, type.duration)
        
        if day.verifyInDisponibility(rangeTime) and doctor.verifyInDisponibility(rangeTime):
            
            roomSelected = None
            for room in rooms:
                if room.verifyInDisponibility(rangeTime):
                    roomSelected = room
            
            if(roomSelected == None):
                return None
            
            return Appointment(
                id=ID(),
                patient=str(patient.id),
                doctor=str(doctor.id),
                room=str(roomSelected.id),
                time=Hour(raw_time),
                type=type,
                status= AppointmentStatus.AVAILABLE,
                rangeTime=rangeTime,
                date = day.date.__str__()
            )

        return None
       
    
    
    
    
    def verifyOverleaps(self, time: RangeTime):
        return self.range_time.overlaps(time.start_time, time.end_time)

    def update(self, data):
        if hasattr(data, "time"):
            self.time = Hour(data.time)
        return self

    @property
    def id(self) -> ID:
        return self._id

    @id.setter
    def id(self, value: ID | str) -> None:
        self._id = value if isinstance(value, ID) else ID(value)

    @property
    def patient_id(self) -> str:
        return self._patient_id

    @patient_id.setter
    def patient_id(self, value: str) -> None:
        self._patient_id = value

    @property
    def doctor_id(self) -> str:
        return self._doctor_id

    @doctor_id.setter
    def doctor_id(self, value: str) -> None:
        self._doctor_id = value

    @property
    def room_id(self) -> str:
        return self._room_id

    @room_id.setter
    def room_id(self, value: str) -> None:
        self._room_id = value

    @property
    def appointment_type(self) -> AppointmentType:
        return self._type

    @appointment_type.setter
    def appointment_type(self, value: AppointmentType) -> None:
        self._type = value

    @property
    def type(self) -> AppointmentType:
        return self._type

    @type.setter
    def type(self, value: AppointmentType) -> None:
        self._type = value

    @property
    def rangeTime(self) -> RangeTime:
        return self._rangeTime

    @rangeTime.setter
    def rangeTime(self, value: RangeTime) -> None:
        self._rangeTime = value

    @property
    def range_time(self) -> RangeTime:
        return self._rangeTime

    @range_time.setter
    def range_time(self, value: RangeTime) -> None:
        self._rangeTime = value

    @property
    def time(self) -> Hour:
        return self._time

    @time.setter
    def time(self, value: Hour | str) -> None:
        self._time = value if isinstance(value, Hour) else Hour(value)

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    @status.setter
    def status(self, value: AppointmentStatus) -> None:
        self._status = value
    
    @property
    def date(self) -> str:
        return self._date

    @date.setter
    def date(self, value: str) -> None:
        self._date = value
    
    
