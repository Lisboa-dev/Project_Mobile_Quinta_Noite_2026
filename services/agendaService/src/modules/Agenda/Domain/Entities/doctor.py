from src.modules.agenda.domain.rules.BaseRule import BaseRule
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime
from ..valueObjects.Id import ID
from ..services.VerifyInRange import VerifyInRange



class Doctor:
   
    
    #id_extern: str,
    def __init__(self, name: str, externId: str | None = None, rules: list[BaseRule] | None = None, id: str | None = None, availability: bool = True):
        self._id = ID(id)
        self._name = name
        self._rules = rules or []
        self._availability = availability
        self._extern_id = externId or str(self._id)
        
        
        
        
    def verifyInDisponibility(self, time: RangeTime) -> bool:
        
        if not self._availability:
            return False
        
        return VerifyInRange.execute(time, self._rules)

        
    def update(self, name: str | None = None, rules: list[BaseRule] | None = None, availability: bool | None = None):
        if name is not None:
            self.name = name
        if rules is not None:
            self.rules = rules
        if availability is not None:
            self.availability = availability
        return self
    
    def delete(self) -> bool:
        self.availability = False
        return True
        
    def updateAvailability(self, availability: bool):
        self.availability = availability
        return self
        

        
        
    def addRule(self, rule: BaseRule):
        self._rules.append(rule)
        
        
    def updateRules(self, rules: list[BaseRule]):
        self.rules = rules
        
    def deleteRule(self, rule: BaseRule):
        self._rules.remove(rule)
        
    
    def addClinicRule(self, rule: BaseRule):
        self._rules.append(rule)
        
        
    def updateClinicRules(self, rules: list[BaseRule]):
        self.rules = rules
        
    def deleteClinicRule(self, rule: BaseRule):
        self._rules.remove(rule)
        
    
    def deleteClinicRules(self):
        self.rules = []

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
    def availability(self) -> bool:
        return self._availability

    @availability.setter
    def availability(self, value: bool) -> None:
        self._availability = bool(value)

    @property
    def extern_id(self) -> str:
        return self._extern_id

    @extern_id.setter
    def extern_id(self, value: str) -> None:
        self._extern_id = value

    @property
    def externId(self) -> str:
        return self._extern_id

    @externId.setter
    def externId(self, value: str) -> None:
        self._extern_id = value
    
    
