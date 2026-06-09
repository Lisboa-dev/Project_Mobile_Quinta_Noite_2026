
from src.modules.agenda.aplication.dtos.exceptions import DeleteUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RuleEvent import DeleteRuleEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository.RuleRepositoryPort import RuleRepositoryPort

class DeleteRuleUseCase:
    def __init__(self, repository: RuleRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, rule_id: str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        
        rule = await self._repository.deleteRule(rule_id)

        if rule is Exception:
            raise DeleteUseCaseException(
                code="DELETE_RULE_ERROR",
                message="Error deleting rule",
                use_case=self.__class__.__name__,
                context={"rule_id": rule_id},
            )

        
        event = DeleteRuleEvent(triggered_by_id=triggered_by_id, rule_id=rule_id)
        await self._bus.emit(event)

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="deleted",
            resource="rule",
            resource_id=rule_id,
            triggered_by_id=triggered_by_id,
            event_name=event.EVENT_NAME,
        )
