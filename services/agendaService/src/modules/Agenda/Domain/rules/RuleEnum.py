from enum import Enum

class RuleEffect(Enum):
    BLOCK = ("BLOCK", 0)
    ADD = ("ADD", 2)
    REMOVE = ("REMOVE", 1)
    NULL = ("NULL", 3)

    def __new__(cls, value: str, priority: int):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.priority = priority
        return obj

    priority: int

    def __str__(self):
        return self.value
    

class TargetType(Enum):
    DOCTOR = "DOCTOR"
    DAY = "DAY"
    ROOM = "ROOM"
    
   
  
