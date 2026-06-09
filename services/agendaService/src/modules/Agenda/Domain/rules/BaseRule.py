
from abc import ABC
from datetime import time
from src.modules.agenda.domain.rules.RuleEnum import RuleEffect, TargetType
from src.modules.agenda.domain.valueObjects.Id import ID
from src.modules.agenda.domain.valueObjects.Date import Date
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime


  
    
class BaseRule(ABC):
    def __init__(
        self,
        ruleEffect: RuleEffect,
        rangeTime: RangeTime | None = None,
        id: str | None = None,
        description: str | None = None,
        date: Date | None = None,
        weekday: int | None = None,
        target: str | None = None,
        targetType: TargetType | None = None,
        nome: str | None = None

      ):
        
        
        self._id= ID()if id==None else id
        self._rangeTime = rangeTime
        self._description = description
        self._date = date
        self._weekday = weekday
        self._ruleEffect = ruleEffect
        self._target = target
        self._targetType = targetType
        self._nome = nome
    
    

    def compare(self, time:RangeTime) -> bool:
        if self._rangeTime is None:
            return False
        return self._rangeTime.compare(time)
    
    @property
    def rangeTime(self) -> RangeTime | None:
        return self._rangeTime

    @rangeTime.setter
    def rangeTime(self, value: RangeTime | None) -> None:
        self._rangeTime = value
    
    @property
    def description(self) -> str | None:
        return self._description
    
    @property
    def date(self) -> Date | None:
        return self._date
    
    @property
    def weekday(self) -> int | None:
        return self._weekday
    
    @property
    def ruleEffect(self) -> RuleEffect:
        return self._ruleEffect
    
    @property
    def ruleEffectPriority(self) -> int:
        return self._ruleEffect.priority
    
    @property
    def startTime(self) -> time | None:
        return self._rangeTime.start_time if self._rangeTime else None
    
    @property
    def endTime(self) -> time | None:
        return self._rangeTime.end_time if self._rangeTime else None
    
    @property
    def target(self) -> str | None:
        return self._target

    @property
    def id(self):
        return self._id

    @property
    def targetType(self) -> TargetType | None:
        return self._targetType

    @property
    def nome(self) -> str | None:
        return self._nome
