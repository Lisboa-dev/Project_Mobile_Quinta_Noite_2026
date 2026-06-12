from ....dtos.useCase.command import CreateMedicCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.medicEvents import MedicCreatedEvent
from ....ports.events import EventBusPort
from ....ports.repository.MedicRepositoryPort import MedicRepositoryPort
from .....domain.entities.MedicEntity import Medic
from .....domain.exceptions.DomainExceptions import UserAlreadyExistsException
from .._helpers import maybe_await, read_value, user_event_payload


class CreateMedicUseCase:
    def __init__(self, repository: MedicRepositoryPort, event_bus: EventBusPort):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, command: CreateMedicCommand) -> UseCaseOutputDTO:
        medic = Medic(
            userName=command.userName,
            email=command.email,
            password=command.password,
            name=command.name,
            crm=command.crm,
        )

        if await maybe_await(self._repository.find_by_username(medic.userName.value)):
            raise UserAlreadyExistsException("userName")
        if await maybe_await(self._repository.find_by_email(medic.email.value)):
            raise UserAlreadyExistsException("email")

        try:
            saved = await maybe_await(self._repository.save(medic))
            event = MedicCreatedEvent(
                **user_event_payload(
                    saved,
                    triggered_by_id=command.triggered_by_id,
                    crm=getattr(saved, "crm", command.crm),
                )
            )
            await maybe_await(self._event_bus.publish(event))
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="created",
                resource="medic",
                resource_id=str(read_value(getattr(medic, "id", None))),
                triggered_by_id=command.triggered_by_id,
                message=str(e),
            )

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="created",
            resource="medic",
            resource_id=str(read_value(getattr(saved, "id", None))),
            triggered_by_id=command.triggered_by_id,
            event_name=event.__class__.__name__,
            message="criacao de medico processada com sucesso",
        )
