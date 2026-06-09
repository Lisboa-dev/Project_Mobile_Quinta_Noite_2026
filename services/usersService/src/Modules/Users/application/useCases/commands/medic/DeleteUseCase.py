from ....dtos.useCase.command import DeleteMedicCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.medicEvents import MedicDeletedEvent
from ....ports.repository.MedicRepositoryPort import MedicRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await, read_value, user_event_payload


class DeleteMedicUseCase:
    def __init__(self, repository: MedicRepositoryPort, event_bus=None):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, command: DeleteMedicCommand) -> UseCaseOutputDTO:
        current = await maybe_await(self._repository.find_by_id(command.id))
        if current is None:
            raise UserNotFoundException(command.id)

        try:
            await maybe_await(self._repository.delete(command.id))
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="medic",
                resource_id=str(command.id),
                triggered_by_id=command.triggered_by_id,
                message=str(e),
            )

        event = MedicDeletedEvent(
            **user_event_payload(
                current,
                triggered_by_id=command.triggered_by_id,
                crm=getattr(current, "crm", None),
            )
        )

        if self._event_bus is not None:
            await maybe_await(self._event_bus.publish(event))

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="deleted",
            resource="medic",
            resource_id=str(read_value(command.id)),
            triggered_by_id=command.triggered_by_id,
            event_name=event.__class__.__name__,
            message="delete de medico processado com sucesso",
        )
