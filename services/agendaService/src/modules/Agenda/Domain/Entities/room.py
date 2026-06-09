from typing import Any
from src.modules.agenda.domain.rules.BaseRule import BaseRule
from src.modules.agenda.domain.services import VerifyInRange
from src.modules.agenda.domain.valueObjects.Id import ID
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime



class Room:

    def __init__(self, name: str, rules: list[BaseRule] | None = None, disponibility: bool = True, id: str | None = None):
        self._name = name
        self._disponibility = disponibility
        self._rules = rules or []
        self._id = ID.generate_id()  if id==None else ID(id)
        self._appointmentList: list[Any] = []
        
  

    def verifyInDisponibility(self, time: RangeTime) -> bool:
        
        if not self._disponibility:
            return False
        
         
        if VerifyInRange.execute(time, self.rules):
            for appointment in self.appointment_list:
                if appointment.verifyOverleaps(time):
                    return False
        else:
            return False
        
        return True

    def update(self, name: str | None = None, rules: list[BaseRule] | None = None, disponibility: bool | None = None):
        if name is not None:
            self.name = name
        if rules is not None:
            self.rules = rules
        if disponibility is not None:
            self.disponibility = disponibility
        return self

    def updateStateRoom(self, data: Any):
        disponibility = getattr(data, "disponibility", None)
        name = getattr(data, "name", None)
        rules = getattr(data, "rules", None)
        return self.update(name=name, rules=rules, disponibility=disponibility)

    def delete(self) -> bool:
        self.disponibility = False
        return True
    
   
       

        
    @property
    def disponibility(self):
        return self._disponibility

    @disponibility.setter
    def disponibility(self, value: bool):
        self._disponibility = bool(value)

    @property
    def id(self) -> ID:
        return self._id

    @id.setter
    def id(self, value: ID | str) -> None:
        self._id = value if isinstance(value, ID) else ID(value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def rules(self) -> list[BaseRule]:
        return self._rules

    @rules.setter
    def rules(self, value: list[BaseRule] | None) -> None:
        self._rules = value or []

    @property
    def appointment_list(self) -> list[Any]:
        return self._appointmentList

    @appointment_list.setter
    def appointment_list(self, value: list[Any] | None) -> None:
        self._appointmentList = value or []

    @property
    def appointmentList(self) -> list[Any]:
        return self._appointmentList

    @appointmentList.setter
    def appointmentList(self, value: list[Any] | None) -> None:
        self._appointmentList = value or []

 
