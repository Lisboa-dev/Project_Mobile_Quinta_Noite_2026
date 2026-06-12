from src.modules.agenda.domain.entities.Room import Room
from src.modules.agenda.domain.services import VerifyInRange
from src.modules.agenda.domain.valueObjects import Date
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime
from src.modules.agenda.domain.valueObjects.EnumDay import DayStatus
from ..rules.BaseRule import BaseRule

class Day:
   
    def __init__(
        self,
        date: Date,
        weekday: int,
        availability: bool,
        status: DayStatus,
        rules: list[BaseRule],
        rooms: list[Room] | None =None
    ):

        self._rooms = [] if rooms is None else rooms
        self._date = date
        self._availability = availability
        
        self._weekday = weekday
        self._status = status
        self._id = date
        self._rules = rules or []
        self._events: list[object] = []
        self._appointmentList_id: list[int] = []
       
        
    def update(self, rooms: list[Room] | dict):
        if isinstance(rooms, dict):
            self.availability = bool(rooms.get("availability", self._availability))
            self.status = rooms.get("status", self._status)
            return self
        self.rooms = rooms
        return self
 
    def updateState(self, newStatus: DayStatus):
        self.status = newStatus
        self.addEvent("objeto de evento")
        
    def createExceptions(self, exceptions: list[RangeTime]):
        self.hoursExceptions = exceptions
        self.addEvent("objeto de evento")
        
    def addAppointment(self, appointment_id: int):
        self.appointment_list_id.append(appointment_id)
        self.addEvent("objeto de evento")
    
    def removeAppointment(self, appointment_id: int):
        self.appointment_list_id.remove(appointment_id)
        self.addEvent("objeto de evento")
    

    
    def verifyInDisponibility(self, time: RangeTime) -> bool:
        if not self._availability:
            return False
     
        return VerifyInRange.execute(time, self._rules)

        
        
        
    
    
    @staticmethod
    def selfCreate(
        rooms: list[Room],
        date: Date,
        weekday: int,
        availability: bool,
        status: DayStatus,
        rules: list[BaseRule],
    ) -> 'Day':
        
        
        for rule in rules:
          
          if (rule.date == date and rule.weekday == None and rule.rangeTime == None):
              availability = False
              status = DayStatus.HOLIDAY
              return Day(
                    rooms=rooms,
                    date=date,
                    weekday=weekday,
                    availability=availability,
                    status=status,
                    rules=[rule]
                )
              
          if(rule.date == None and rule.weekday == weekday and rule.rangeTime == None):
              availability = False
              status = DayStatus.HOLIDAY
              return Day(
                    rooms=rooms,
                    date=date,
                    weekday=weekday,
                    availability=availability,
                    status=status,
                    rules=[rule]
                )
       
    
        
        obj =Day(
            rooms=rooms,
            date=date,
            weekday=weekday,
            availability=availability,
            status=status,
            rules=rules
        )
        
        obj.addEvent("objeto de evento")
        return obj
        
    
    
    def addRules(self, rules: list[BaseRule]):
        self.rules.extend(rules)

    def addEvent(self, event):
        self._events.append(event)

    @property
    def rooms(self) -> list[Room]:
        return self._rooms

    @rooms.setter
    def rooms(self, value: list[Room] | None) -> None:
        self._rooms = value or []

    @property
    def id(self) -> Date:
        return self._id

    @id.setter
    def id(self, value: Date) -> None:
        self._id = value

    @property
    def date(self) -> Date:
        return self._date

    @date.setter
    def date(self, value: Date) -> None:
        self._date = value
        self._id = value

    @property
    def weekday(self) -> int:
        return self._weekday

    @weekday.setter
    def weekday(self, value: int) -> None:
        self._weekday = value

    @property
    def availability(self) -> bool:
        return self._availability

    @availability.setter
    def availability(self, value: bool) -> None:
        self._availability = bool(value)

    @property
    def status(self) -> DayStatus:
        return self._status

    @status.setter
    def status(self, value: DayStatus) -> None:
        self._status = value

    @property
    def rules(self) -> list[BaseRule]:
        return self._rules

    @rules.setter
    def rules(self, value: list[BaseRule] | None) -> None:
        self._rules = value or []

    @property
    def events(self) -> list[object]:
        return self._events

    @events.setter
    def events(self, value: list[object] | None) -> None:
        self._events = value or []

    @property
    def appointment_list_id(self) -> list[int]:
        return self._appointmentList_id

    @appointment_list_id.setter
    def appointment_list_id(self, value: list[int] | None) -> None:
        self._appointmentList_id = value or []

    @property
    def appointmentList_id(self) -> list[int]:
        return self._appointmentList_id

    @appointmentList_id.setter
    def appointmentList_id(self, value: list[int] | None) -> None:
        self._appointmentList_id = value or []
        
    
    
