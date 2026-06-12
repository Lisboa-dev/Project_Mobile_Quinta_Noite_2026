from .appointment import CreateAppointmentRequest, DeleteAppointmentRequest, UpdateAppointmentRequest
from .calendar import CreateCalendarRequest, UpdateDayRequest
from .clinic import CreateClinicRequest, UpdateClinicRequest
from .doctor import CreateDoctorRequest, UpdateDoctorRequest
from .infra import InfraEventRequest
from .patient import CreatePatientRequest, UpdatePatientRequest
from .room import CreateRoomRequest, UpdateRoomRequest
from .rule import (
    CreateBlockRuleRequest,
    CreateGenericRuleRequest,
    CreateSpecificDayRuleRequest,
    CreateSpecificRuleRequest,
    CreateWeekRuleRequest,
)

__all__ = [
    "CreateAppointmentRequest",
    "CreateBlockRuleRequest",
    "CreateCalendarRequest",
    "CreateClinicRequest",
    "CreateDoctorRequest",
    "CreateGenericRuleRequest",
    "CreatePatientRequest",
    "CreateRoomRequest",
    "CreateSpecificDayRuleRequest",
    "CreateSpecificRuleRequest",
    "CreateWeekRuleRequest",
    "DeleteAppointmentRequest",
    "InfraEventRequest",
    "UpdateAppointmentRequest",
    "UpdateClinicRequest",
    "UpdateDayRequest",
    "UpdateDoctorRequest",
    "UpdatePatientRequest",
    "UpdateRoomRequest",
]
