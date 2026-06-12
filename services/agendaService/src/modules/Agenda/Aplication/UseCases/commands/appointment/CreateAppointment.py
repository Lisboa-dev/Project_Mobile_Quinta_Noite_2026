from src.modules.agenda.domain.entities import Doctor
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.repositorys.input import AppointmentSchedulingInputDTO
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.AppointmentEvent import CreateAppointmentEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository.AppointmentRepositoryPort import AppointmentRepositoryPort
from src.modules.agenda.aplication.ports.repository.AppointmentSchedulingRepositoryPort import AppointmentSchedulingRepositoryPort
from src.modules.agenda.aplication.ports.repository.CalendarRepositoryPort import CalendarRepositoryPort
from src.modules.agenda.aplication.dtos.useCase.command.AppointmentUseCasesDTO import CreateAppointmentCommand
from src.modules.agenda.aplication.useCases._context import command_to_context
from src.modules.agenda.domain.entities import Appointment
from src.modules.agenda.domain.valueObjects.Date import Date
from src.modules.agenda.domain.valueObjects.EnumDay import DayStatus

class CreateAppointmentUseCase:
    def __init__(
        self,
        repositoryAppointment: AppointmentRepositoryPort,
        repositorySchedulingContext: AppointmentSchedulingRepositoryPort,
        repositoryCalendar: CalendarRepositoryPort,
        bus: BusPort,
    ):
        self._repositoryAppointment = repositoryAppointment
        self._repositorySchedulingContext = repositorySchedulingContext
        self._repositoryCalendar = repositoryCalendar
        self._bus = bus
        
    async def execute(self, command:CreateAppointmentCommand) -> UseCaseOutputDTO:
        try:
            
            if  Date.stringToObject(command.date).isBefore(Date.toDay()):
                raise Exception("Date cannot be before today")
            
            
            print("antes de executar context \n\n\n\n\n")
            print(command)
            
            context = await self._repositorySchedulingContext.getContext(
               
                AppointmentSchedulingInputDTO(
                    date=command.date, 
                    weekday=command.weekday, 
                    doctor=command.doctor, 
                    patient=command.patient, 
                    time=command.time,
                    type=command.type,
                )
            )
            print("depois de executar context \n\n\n\n\n")
            print(context)
            
            appointment = None
            
            for appointment in context.appointmentsToDoctor:
                appointment.verifyOverleaps(context.rangeTime)
                
            for appointment in context.appointmentsToPatient:
                appointment.verifyOverleaps(context.rangeTime)
                
            
            
            if context.day.verifyInDisponibility(context.rangeTime):
               if context.doctor.verifyInDisponibility(context.rangeTime):
                   for room in context.rooms:
                       if room.verifyInDisponibility(context.rangeTime):
                       
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
                await self._sync_day_after_appointment(context.day, context.room, appointment)
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

    async def _sync_day_after_appointment(self, day, rooms, appointment: Appointment) -> None:
        persisted_day = await self._repositoryCalendar.get(str(day.id)) or day
        persisted_day.addAppointment(str(appointment.id))  # type: ignore[arg-type]

        for room in rooms:
            if str(room.id) == str(appointment.room_id):
                room.appointment_list = list(room.appointment_list) + [appointment]

        has_available_room_for_slot = any(
            room.verifyInDisponibility(appointment.rangeTime)
            for room in rooms
        )

        if not persisted_day.verifyInDisponibility(appointment.rangeTime) or not has_available_room_for_slot:
            persisted_day.availability = False
            persisted_day.status = DayStatus.SCHEDULED

        await self._repositoryCalendar.updateDay(persisted_day)
      
    
