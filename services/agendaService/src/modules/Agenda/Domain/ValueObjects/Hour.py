
from datetime import datetime



class Hour:
    TIME_PATTERN = "%H:%M"
     
    def __init__(self, hour: str | None = None) -> None:
        self.hour = hour or datetime.now().strftime(self.TIME_PATTERN)
        self._validate(self.hour)
        
    
    def compare(self, hour: str) -> bool:
        return self.hour == hour

    def __str__(self) -> str:
        return self.hour

    def _validate(self, value: str) -> None:
        datetime.strptime(value, self.TIME_PATTERN)
