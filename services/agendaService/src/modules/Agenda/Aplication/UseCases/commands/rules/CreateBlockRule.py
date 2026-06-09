from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.command.RulesUseCasesDTO import CreateBlockRuleCommand
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RuleEvent import CreateBlockRuleEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import RuleRepositoryPort
from src.modules.agenda.domain.rules.BlockRule import BlockRule


class CreateBlockRuleUseCase:
    def __init__(self, repository: RuleRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus

    async def execute(self, command: CreateBlockRuleCommand) -> UseCaseOutputDTO:
        try:
            rule = BlockRule(
                date=command.date,  # type: ignore[arg-type]
                weekday=command.weekday,
                description=command.description,
                target=command.target,
                targetType=command.targetType,  # type: ignore[arg-type]
                nome=command.nome,
            )
            await self._repository.save(rule)
            event = CreateBlockRuleEvent.from_entity(rule, triggered_by_id=command.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="block_rule",
                resource_id=str(rule.id),
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_BLOCK_RULE_ERROR",
                message="Error creating block rule",
                use_case=self.__class__.__name__,
                context={"command": str(command)},
                original=e,
            ) from e
