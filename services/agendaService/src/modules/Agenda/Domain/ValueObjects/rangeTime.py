from __future__ import annotations

from datetime import datetime, time, timedelta
from src.modules.agenda.domain.exceptions import (
    InvalidTimeFormatException,
    InvalidTimeRangeException,
    MissingTimeBoundaryException,
)


class RangeTime:

    TIME_PATTERN = "%H:%M"

    def __init__(
        self,
        start_time: str | time,
        end_time: str | time
    ):

        self.start_time = self._validate_time(start_time)
        self.end_time = self._validate_time(end_time) 

        if self.start_time >= self.end_time:
            raise InvalidTimeRangeException(
                "start_time must be lower than end_time",
                {"start_time": start_time, "end_time": end_time},
            )



    def _validate_time(self, value: str | time) -> time:
        if isinstance(value, time):
            return value
        value = str(value)
        try:
            return datetime.strptime(
                value,
                self.TIME_PATTERN
            ).time()

        except ValueError as exc:
            raise InvalidTimeFormatException(
                f"Invalid time format. Use {self.TIME_PATTERN}",
                {"value": value, "pattern": self.TIME_PATTERN},
            ) from exc

    def __str__(self):
        return (
            f"{self.start_time.strftime(self.TIME_PATTERN)}"
            f" - "
            f"{self.end_time.strftime(self.TIME_PATTERN)}"
        )

    def compare(self, start_time: str | time | 'RangeTime' | None, end_time: str | time | None = None):
        
        if start_time is None:
            raise MissingTimeBoundaryException(
                "start_time is required when comparing raw time values",
                {"end_time": end_time},
            )

        if isinstance(start_time, RangeTime):
            return self.start_time == start_time.start_time and self.end_time == start_time.end_time

        if end_time is None:
            raise MissingTimeBoundaryException(
                "end_time is required when comparing raw time values",
                {"start_time": start_time},
            )

        start_obj = self._validate_time(start_time)
        end_obj = self._validate_time(end_time)

        return (
            self.start_time == start_obj
            and
            self.end_time == end_obj
        )

    def overlaps(self, start_time: str | time | 'RangeTime', end_time: str | time | None = None):
        if isinstance(start_time, RangeTime):
            start = start_time.start_time
            end = start_time.end_time
        else:
            if end_time is None:
                raise MissingTimeBoundaryException(
                    "end_time is required when checking overlap with raw time values",
                    {"start_time": start_time},
                )
            start = self._validate_time(start_time)
            end = self._validate_time(end_time)

        return start < self.end_time and end > self.start_time
           

        
    @staticmethod
    def generate(time_str: str, duration: int) -> 'RangeTime':
        time_str = str(time_str)
        start = datetime.strptime(time_str, "%H:%M")
        end = start + timedelta(minutes=duration)

        return RangeTime(
            start.strftime("%H:%M"),
            end.strftime("%H:%M")
        )


    @staticmethod
    def _format(value: time) -> str:
        return value.strftime(RangeTime.TIME_PATTERN)

    @staticmethod
    def fusion( other: 'RangeTime', other2: 'RangeTime') ->'RangeTime' | None:
        
             
        timeInit1 = other.start_time
        timeEnd1 = other.end_time
        
        timeInit2 = other2.start_time
        timeEnd2 = other2.end_time
            
            
     
        if((timeInit1<=timeInit2 and timeInit1<timeEnd2)and(timeEnd1<timeInit2 and timeEnd1<timeEnd2))or((timeInit2<timeInit1 and timeInit2<timeEnd1)and(timeEnd2<timeInit1 and timeEnd2<timeEnd1)):
            return None
     
     
        if other2.overlaps(other.start_time, other.end_time):
           return other2
        
        if other.overlaps(other2.start_time, other2.end_time):
            return other
           
            
        timeInit1 = other.start_time
        timeEnd1 = other.end_time
        
        timeInit2 = other2.start_time
        timeEnd2 = other2.end_time
            
            
        
        if (timeInit1 == timeInit2 and timeEnd1 == timeEnd2):
            return RangeTime(other.start_time, other.end_time)
        
        
        start_time = min( other.start_time, other2.start_time)
        end_time = max(other.end_time, other.end_time, other2.end_time)
        
        return RangeTime(start_time, end_time)
    
    
    
    
    
    @staticmethod
    def subtract( base: 'RangeTime', sub: 'RangeTime') -> list['RangeTime']:
        
          
        baseInit = base.start_time
        baseEnd = base.end_time
        
        subInit = sub.start_time
        subEnd = sub.end_time
        
        
        if not base.overlaps(sub.start_time, sub.end_time):
            
            if(baseInit == subInit):
                return[RangeTime(sub.end_time, base.end_time)]
            if(baseEnd == subEnd):
                return[RangeTime(base.start_time, sub.start_time)]
            
            return [RangeTime(base.start_time, sub.start_time), RangeTime(sub.end_time, base.end_time)]
        
        if base.compare(sub.start_time, sub.end_time) or sub.overlaps(base.start_time, base.end_time):
            return []
        
        
        
        if (baseInit < subInit and subInit < baseEnd and baseEnd < subEnd):
            return [RangeTime(base.start_time, sub.start_time)]
        
        if (subInit < baseInit and baseInit < subEnd and subEnd < baseEnd):
            return [RangeTime(sub.end_time, base.end_time)]

        return []
        
        
        
        
        
        
