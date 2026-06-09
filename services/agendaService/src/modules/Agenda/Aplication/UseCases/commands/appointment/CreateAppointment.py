from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.repositorys.input import AppointmentSchedulingInputDTO
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.AppointmentEvent import CreateAppointmentEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository.AppointmentRepositoryPort import AppointmentRepositoryPort
from src.modules.agenda.aplication.ports.repository.AppointmentSchedulingRepositoryPort import AppointmentSchedulingRepositoryPort
from src.modules.agenda.aplication.dtos.useCase.command.AppointmentUseCasesDTO import CreateAppointmentCommand
from src.modules.agenda.aplication.useCases._context import command_to_context
from src.modules.agenda.domain.entities import Appointment
from src.modules.agenda.domain.valueObjects.Date import Date

class CreateAppointmentUseCase:
    def __init__(self, repositoryAppointment: AppointmentRepositoryPort, repositorySchedulingContext: AppointmentSchedulingRepositoryPort, bus: BusPort):
        self._repositoryAppointment = repositoryAppointment
        self._repositorySchedulingContext = repositorySchedulingContext
        self._bus = bus
        
    async def execute(self, command:CreateAppointmentCommand) -> UseCaseOutputDTO:
        try:
            
            if Date.stringToObject(command.date).isBefore(Date.today()):
                raise Exception("Date cannot be before today")
                
            context = await self._repositorySchedulingContext.getContext(
                AppointmentSchedulingInputDTO(
                    date=command.date, 
                    weekday=command.weekday, 
                    doctor=command.doctor, 
                    patient=command.patient, 
                    room=command.room,
                    time=command.time,
                    type=command.type,
                )
            )
            
            appointment = Appointment.create(
                patient=context.patient,
                doctor=context.doctor,
                rooms=context.room,
                day=context.day,
                time=context.time,
                type=context.type
            )
           
            if isinstance(appointment, Appointment):
                await self._repositoryAppointment.save(appointment, command.scheduler_id)
                event = CreateAppointmentEvent.from_entity(
                    appointment,
                    triggered_by_id=command.triggered_by_id,
                    scheduler_id=command.scheduler_id,
                )
                await self._bus.emit(event)
                return UseCaseOutputDTO.ok(
                    use_case=self.__class__.__name__,
                    action="created",
                    resource="appointment",
                    resource_id=str(appointment.id),
                    triggered_by_id=command.triggered_by_id,
                    event_name=event.EVENT_NAME,
                    data={
                        "doctor_id": str(appointment.doctor_id),
                        "patient_id": str(appointment.patient_id),
                        "room_id": str(appointment.room_id),
                        "scheduler_id": command.scheduler_id,
                    },
                )
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="create",
                resource="appointment",
                triggered_by_id=command.triggered_by_id,
                message="Appointment could not be created for the requested slot",
            )
            
            
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_APPOINTMENT_ERROR",
                message="Error creating appointment",
                use_case=self.__class__.__name__,
                context={"command": command_to_context(command)},
                original=e,
            ) from e
      
    
