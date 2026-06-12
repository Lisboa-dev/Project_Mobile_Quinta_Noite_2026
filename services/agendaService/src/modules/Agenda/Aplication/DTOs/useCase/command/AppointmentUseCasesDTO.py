from dataclasses import dataclass


@dataclass(frozen=True)
class CreateAppointmentCommand:
    scheduler_id: str
    date:str
    weekday:str
    doctor:str
    patient:str
    time:str
    type:str
    triggered_by_id: str | None = None

    
    
@dataclass(frozen=True)
class DeleteAppointmentCommand:
    id: str
    triggered_by_id: str | None = None
    
@dataclass(frozen=True)
class UpdateAppointmentCommand:
    id: str
    triggered_by_id: str | None = None

@dataclass(frozen=True)
class UpdateAppointmentDateCommand:
    id: str
    nome:str 
    time:str
    date:str
    triggered_by_id: str | None = None
    
@dataclass(frozen=True)
class CreateAppointmentTypeCommand:
    name: str
    duration: int
    description: str 
    triggered_by_id: str | None = None
