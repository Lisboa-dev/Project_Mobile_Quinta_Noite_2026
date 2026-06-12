from functools import lru_cache
from typing import cast

from src.infra.adapter.repository import (
    AgendaRepository,
    AppointmentRepository,
    AppointmentSchedulingRepository,
    CalendarRepository,
    ClinicRepository,
    DoctorRepository,
    PatientRepository,
    RoomRepository,
    RuleRepository,
)

from src.infra.adapter.ExternServices import CalendarDataClient
from src.infra.adapter.Messaging import InMemoryEventBus
from src.infra.adapter.Messaging.websocket.container import connection_manager
from src.infra.adapter.Messaging.rabbitMQ.userServiceConsumers import UserServiceCreatedEventsConsumer
from src.infra.adapter.repository.querys import (
    AppointmentQueryRepository,
    AppointmentTypeQueryRepository,
    CalendarQueryRepository,
    ClinicQueryRepository,
    DoctorQueryRepository,
    PatientQueryRepository,
    RoomQueryRepository,
    RuleQueryRepository,
)
from src.infra.clients import DatadogClient, PostgresClient, PrometheusClient, RabbitMQClient, RedisClient
from src.infra.config.settings import settings
from src.infra.handlers import (
    InfraHealthHandler,
    UserServiceDoctorCreatedHandler,
    UserServiceDoctorDeletedHandler,
    UserServicePatientCreatedHandler,
    UserServicePatientDeletedHandler,
)
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.externServices.CalendarDataPort import CalendarDataPort
from src.modules.agenda.aplication.ports.repository import (
    AppointmentRepositoryPort,
    AppointmentSchedulingRepositoryPort,
    CalendarRepositoryPort,
    ClinicRepositoryPort,
    DoctorRepositoryPort,
    PatientRepositoryPort,
    RoomRepositoryPort,
    RuleRepositoryPort,
)
from src.modules.agenda.aplication.ports.repository.querys import (
    AppointmentQueryRepositoryPort,
    AppointmentTypeQueryRepositoryPort,
    CalendarQueryRepositoryPort,
    ClinicQueryRepositoryPort,
    DoctorQueryRepositoryPort,
    PatientQueryRepositoryPort,
    RoomQueryRepositoryPort,
    RuleQueryRepositoryPort,
)
from src.modules.agenda.aplication.useCases.commands.appointment.CreateAppointment import (
    CreateAppointmentUseCase,
)
from src.modules.agenda.aplication.useCases.commands.appointment.CreateAppointmentType import (
    CreateAppointmentTypeUseCase,
)
from src.modules.agenda.aplication.useCases.commands.appointment.DeleteAppointment import (
    DeleteAppointmentUseCase,
)
from src.modules.agenda.aplication.useCases.commands.appointment.UpdateAppointment import (
    UpdateAppointmentUseCase,
)
from src.modules.agenda.aplication.useCases.commands.calendar.CreateCalendar import (
    CreateCalendarUseCase,
)
from src.modules.agenda.aplication.useCases.commands.calendar.DeleteCalendar import (
    DeleteCalendarUseCase,
)
from src.modules.agenda.aplication.useCases.commands.calendar.UpdateDay import (
    UpdateDayUseCase,
)
from src.modules.agenda.aplication.useCases.commands.clinic.CreateClinic import (
    CreateClinicUseCase,
)
from src.modules.agenda.aplication.useCases.commands.clinic.DeleteClinic import (
    DeleteClinicUseCase,
)
from src.modules.agenda.aplication.useCases.commands.doctor.CreateDoctor import (
    CreateDoctorUseCase,
)
from src.modules.agenda.aplication.useCases.commands.doctor.DeleteDoctor import (
    DeleteDoctorUseCase,
)
from src.modules.agenda.aplication.useCases.commands.doctor.UpdateDoctor import (
    UpdateDoctorUseCase,
)
from src.modules.agenda.aplication.useCases.commands.patient.CreatePacient import (
    CreatePatientUseCase,
)
from src.modules.agenda.aplication.useCases.commands.patient.DeletePacient import (
    DeletePatientUseCase,
)
from src.modules.agenda.aplication.useCases.commands.room.CreateRoom import (
    CreateRoomUseCase,
)
from src.modules.agenda.aplication.useCases.commands.room.DeleteRoom import (
    DeleteRoomUseCase,
)
from src.modules.agenda.aplication.useCases.commands.room.UpdateStateRoom import (
    UpdateRoomUseCase,
)
from src.modules.agenda.aplication.useCases.commands.rules.CreateBlockRule import (
    CreateBlockRuleUseCase,
)
from src.modules.agenda.aplication.useCases.commands.rules.CreateGenericRule import (
    CreateGenericRuleUseCase,
)
from src.modules.agenda.aplication.useCases.commands.rules.CreateSpecificEntityRule import (
    CreateSpecificDayRuleUseCase,
)
from src.modules.agenda.aplication.useCases.commands.rules.CreateSpecificRule import (
    CreateSpecificRuleUseCase,
)
from src.modules.agenda.aplication.useCases.commands.rules.CreateWeekRule import (
    CreateWeekRuleUseCase,
)
from src.modules.agenda.aplication.useCases.commands.rules.DeleteRule import (
    DeleteRuleUseCase,
)
from src.modules.agenda.aplication.useCases.querys import (
    GetAppointmentByIdUseCase,
    GetAppointmentTypeByIdUseCase,
    GetClinicByIdUseCase,
    GetDayByIdUseCase,
    GetDoctorByIdUseCase,
    GetPatientByIdUseCase,
    GetRoomAdminDetailUseCase,
    GetRoomByIdUseCase,
    GetRuleByIdUseCase,
    GetRulesAdminContextUseCase,
    ListAppointmentTypesUseCase,
    ListAppointmentsByDoctorUseCase,
    ListAppointmentsByPatientUseCase,
    ListAppointmentsUseCase,
    ListClinicsUseCase,
    ListDaysUseCase,
    ListDoctorsUseCase,
    ListMonthDaysForFrontUseCase,
    ListPatientsUseCase,
    ListRoomsAdminDetailedUseCase,
    ListRoomsUseCase,
    ListRulesUseCase,
)


@lru_cache
def get_event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@lru_cache
def get_agenda_repository() -> AgendaRepository:
    return AgendaRepository()


@lru_cache
def get_appointment_repository() -> AppointmentRepository:
    return AppointmentRepository()


@lru_cache
def get_appointment_scheduling_repository() -> AppointmentSchedulingRepository:
    return AppointmentSchedulingRepository()


@lru_cache
def get_calendar_repository() -> CalendarRepository:
    return CalendarRepository()


@lru_cache
def get_rule_repository() -> RuleRepository:
    return RuleRepository()


@lru_cache
def get_calendar_data_client() -> CalendarDataClient:
    return CalendarDataClient()


@lru_cache
def get_clinic_repository() -> ClinicRepository:
    return ClinicRepository()


@lru_cache
def get_doctor_repository() -> DoctorRepository:
    return DoctorRepository()


@lru_cache
def get_patient_repository() -> PatientRepository:
    return PatientRepository()


@lru_cache
def get_room_repository() -> RoomRepository:
    return RoomRepository()


@lru_cache
def get_rabbitmq_client() -> RabbitMQClient:
    return RabbitMQClient()


@lru_cache
def get_user_events_rabbitmq_client() -> RabbitMQClient:
    return RabbitMQClient(exchange_name=settings.user_events_exchange)


@lru_cache
def get_postgres_client() -> PostgresClient:
    return PostgresClient()


@lru_cache
def get_redis_client() -> RedisClient:
    return RedisClient()


@lru_cache
def get_prometheus_client() -> PrometheusClient:
    return PrometheusClient()


@lru_cache
def get_datadog_client() -> DatadogClient:
    return DatadogClient()


@lru_cache
def get_appointment_query_repository() -> AppointmentQueryRepository:
    return AppointmentQueryRepository()


@lru_cache
def get_appointment_type_query_repository() -> AppointmentTypeQueryRepository:
    return AppointmentTypeQueryRepository()


@lru_cache
def get_calendar_query_repository() -> CalendarQueryRepository:
    return CalendarQueryRepository()


@lru_cache
def get_clinic_query_repository() -> ClinicQueryRepository:
    return ClinicQueryRepository()


@lru_cache
def get_doctor_query_repository() -> DoctorQueryRepository:
    return DoctorQueryRepository()


@lru_cache
def get_patient_query_repository() -> PatientQueryRepository:
    return PatientQueryRepository()


@lru_cache
def get_room_query_repository() -> RoomQueryRepository:
    return RoomQueryRepository()


@lru_cache
def get_rule_query_repository() -> RuleQueryRepository:
    return RuleQueryRepository()


def get_create_appointment_use_case() -> CreateAppointmentUseCase:
    return CreateAppointmentUseCase(
        cast(AppointmentRepositoryPort, get_appointment_repository()),
        cast(AppointmentSchedulingRepositoryPort, get_appointment_scheduling_repository()),
        cast(CalendarRepositoryPort, get_calendar_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_update_appointment_use_case() -> UpdateAppointmentUseCase:
    return UpdateAppointmentUseCase(
        cast(AppointmentRepositoryPort, get_appointment_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_appointment_use_case() -> DeleteAppointmentUseCase:
    return DeleteAppointmentUseCase(
        cast(AppointmentRepositoryPort, get_appointment_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_appointment_type_use_case() -> CreateAppointmentTypeUseCase:
    return CreateAppointmentTypeUseCase(
        cast(AppointmentRepositoryPort, get_appointment_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_calendar_use_case() -> CreateCalendarUseCase:
    return CreateCalendarUseCase(
        cast(CalendarRepositoryPort, get_calendar_repository()),
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(CalendarDataPort, get_calendar_data_client()),
        cast(BusPort, get_event_bus()),
    )


def get_update_day_use_case() -> UpdateDayUseCase:
    return UpdateDayUseCase(
        cast(CalendarRepositoryPort, get_calendar_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_calendar_use_case() -> DeleteCalendarUseCase:
    return DeleteCalendarUseCase(cast(CalendarRepositoryPort, get_calendar_repository()), get_event_bus())


def get_create_clinic_use_case() -> CreateClinicUseCase:
    return CreateClinicUseCase(
        cast(ClinicRepositoryPort, get_clinic_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_clinic_use_case() -> DeleteClinicUseCase:
    return DeleteClinicUseCase(
        cast(ClinicRepositoryPort, get_clinic_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_doctor_use_case() -> CreateDoctorUseCase:
    return CreateDoctorUseCase(
        cast(DoctorRepositoryPort, get_doctor_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_update_doctor_use_case() -> UpdateDoctorUseCase:
    return UpdateDoctorUseCase(
        cast(DoctorRepositoryPort, get_doctor_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_doctor_use_case() -> DeleteDoctorUseCase:
    return DeleteDoctorUseCase(
        cast(DoctorRepositoryPort, get_doctor_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_patient_use_case() -> CreatePatientUseCase:
    return CreatePatientUseCase(
        cast(PatientRepositoryPort, get_patient_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_patient_use_case() -> DeletePatientUseCase:
    return DeletePatientUseCase(
        cast(PatientRepositoryPort, get_patient_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_room_use_case() -> CreateRoomUseCase:
    return CreateRoomUseCase(
        cast(RoomRepositoryPort, get_room_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_update_room_use_case() -> UpdateRoomUseCase:
    return UpdateRoomUseCase(
        cast(RoomRepositoryPort, get_room_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_room_use_case() -> DeleteRoomUseCase:
    return DeleteRoomUseCase(
        cast(RoomRepositoryPort, get_room_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_block_rule_use_case() -> CreateBlockRuleUseCase:
    return CreateBlockRuleUseCase(
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_generic_rule_use_case() -> CreateGenericRuleUseCase:
    return CreateGenericRuleUseCase(
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_specific_rule_use_case() -> CreateSpecificRuleUseCase:
    return CreateSpecificRuleUseCase(
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_specific_day_rule_use_case() -> CreateSpecificDayRuleUseCase:
    return CreateSpecificDayRuleUseCase(
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_create_week_rule_use_case() -> CreateWeekRuleUseCase:
    return CreateWeekRuleUseCase(
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_delete_rule_use_case() -> DeleteRuleUseCase:
    return DeleteRuleUseCase(
        cast(RuleRepositoryPort, get_rule_repository()),
        cast(BusPort, get_event_bus()),
    )


def get_appointment_by_id_query_use_case() -> GetAppointmentByIdUseCase:
    return GetAppointmentByIdUseCase(
        cast(AppointmentQueryRepositoryPort, get_appointment_query_repository())
    )


def get_list_appointments_query_use_case() -> ListAppointmentsUseCase:
    return ListAppointmentsUseCase(
        cast(AppointmentQueryRepositoryPort, get_appointment_query_repository())
    )


def get_list_appointments_by_patient_query_use_case() -> ListAppointmentsByPatientUseCase:
    return ListAppointmentsByPatientUseCase(
        cast(AppointmentQueryRepositoryPort, get_appointment_query_repository())
    )


def get_list_appointments_by_doctor_query_use_case() -> ListAppointmentsByDoctorUseCase:
    return ListAppointmentsByDoctorUseCase(
        cast(AppointmentQueryRepositoryPort, get_appointment_query_repository())
    )


def get_appointment_type_by_id_query_use_case() -> GetAppointmentTypeByIdUseCase:
    return GetAppointmentTypeByIdUseCase(
        cast(AppointmentTypeQueryRepositoryPort, get_appointment_type_query_repository())
    )


def get_list_appointment_types_query_use_case() -> ListAppointmentTypesUseCase:
    return ListAppointmentTypesUseCase(
        cast(AppointmentTypeQueryRepositoryPort, get_appointment_type_query_repository())
    )


def get_day_by_id_query_use_case() -> GetDayByIdUseCase:
    return GetDayByIdUseCase(cast(CalendarQueryRepositoryPort, get_calendar_query_repository()))


def get_list_days_query_use_case() -> ListDaysUseCase:
    return ListDaysUseCase(cast(CalendarQueryRepositoryPort, get_calendar_query_repository()))


def get_list_month_days_for_front_query_use_case() -> ListMonthDaysForFrontUseCase:
    return ListMonthDaysForFrontUseCase(cast(CalendarQueryRepositoryPort, get_calendar_query_repository()))


def get_clinic_by_id_query_use_case() -> GetClinicByIdUseCase:
    return GetClinicByIdUseCase(cast(ClinicQueryRepositoryPort, get_clinic_query_repository()))


def get_list_clinics_query_use_case() -> ListClinicsUseCase:
    return ListClinicsUseCase(cast(ClinicQueryRepositoryPort, get_clinic_query_repository()))


def get_doctor_by_id_query_use_case() -> GetDoctorByIdUseCase:
    return GetDoctorByIdUseCase(cast(DoctorQueryRepositoryPort, get_doctor_query_repository()))


def get_list_doctors_query_use_case() -> ListDoctorsUseCase:
    return ListDoctorsUseCase(cast(DoctorQueryRepositoryPort, get_doctor_query_repository()))


def get_patient_by_id_query_use_case() -> GetPatientByIdUseCase:
    return GetPatientByIdUseCase(cast(PatientQueryRepositoryPort, get_patient_query_repository()))


def get_list_patients_query_use_case() -> ListPatientsUseCase:
    return ListPatientsUseCase(cast(PatientQueryRepositoryPort, get_patient_query_repository()))


def get_room_by_id_query_use_case() -> GetRoomByIdUseCase:
    return GetRoomByIdUseCase(cast(RoomQueryRepositoryPort, get_room_query_repository()))


def get_list_rooms_query_use_case() -> ListRoomsUseCase:
    return ListRoomsUseCase(cast(RoomQueryRepositoryPort, get_room_query_repository()))


def get_room_admin_detail_query_use_case() -> GetRoomAdminDetailUseCase:
    return GetRoomAdminDetailUseCase(cast(RoomQueryRepositoryPort, get_room_query_repository()))


def get_list_rooms_admin_detailed_query_use_case() -> ListRoomsAdminDetailedUseCase:
    return ListRoomsAdminDetailedUseCase(cast(RoomQueryRepositoryPort, get_room_query_repository()))


def get_rule_by_id_query_use_case() -> GetRuleByIdUseCase:
    return GetRuleByIdUseCase(cast(RuleQueryRepositoryPort, get_rule_query_repository()))


def get_list_rules_query_use_case() -> ListRulesUseCase:
    return ListRulesUseCase(cast(RuleQueryRepositoryPort, get_rule_query_repository()))


def get_rules_admin_context_query_use_case() -> GetRulesAdminContextUseCase:
    return GetRulesAdminContextUseCase(cast(RuleQueryRepositoryPort, get_rule_query_repository()))


def get_connection_manager():
    return connection_manager


def get_infra_health_handler() -> InfraHealthHandler:
    return InfraHealthHandler(get_event_bus())


def get_user_service_doctor_created_handler() -> UserServiceDoctorCreatedHandler:
    return UserServiceDoctorCreatedHandler(get_create_doctor_use_case())


def get_user_service_patient_created_handler() -> UserServicePatientCreatedHandler:
    return UserServicePatientCreatedHandler(get_create_patient_use_case())


def get_user_service_doctor_deleted_handler() -> UserServiceDoctorDeletedHandler:
    return UserServiceDoctorDeletedHandler(get_delete_doctor_use_case())


def get_user_service_patient_deleted_handler() -> UserServicePatientDeletedHandler:
    return UserServicePatientDeletedHandler(get_delete_patient_use_case())


def get_user_service_created_events_consumer() -> UserServiceCreatedEventsConsumer:
    return UserServiceCreatedEventsConsumer(
        rabbitmq=get_user_events_rabbitmq_client(),
        doctor_created_handler=get_user_service_doctor_created_handler(),
        patient_created_handler=get_user_service_patient_created_handler(),
        doctor_deleted_handler=get_user_service_doctor_deleted_handler(),
        patient_deleted_handler=get_user_service_patient_deleted_handler(),
    )
