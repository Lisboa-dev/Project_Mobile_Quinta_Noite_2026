from uuid import UUID
from datetime import datetime
from enum import Enum


class DayStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SCHEDULED = "SCHEDULED"
    BLOCKED = "BLOCKED"
    HOLIDAY = "HOLIDAY"
    UNAVAILABLE = "UNAVAILABLE"
    