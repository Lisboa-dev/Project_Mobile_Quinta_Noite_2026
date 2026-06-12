
from .AppointmentController import routerAppointment
from .CalendarController import routerCalendar
from .ClinicController import routerClinic
from .InfraController import routerInfra
from .RoomController import routerRoom
from .RuleController import routerRule
from .WebsocketController import router as routerWebsocket

__all__ = [
    "routerAppointment",
    "routerCalendar",
    "routerClinic",
    "routerInfra",
    "routerRoom",
    "routerRule",
    "routerWebsocket",
]
