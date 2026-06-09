from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.command.RulesUseCasesDTO import CreateGenericRuleCommand
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RuleEvent import CreateGenericRuleEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import RuleRepositoryPort
from src.modules.agenda.domain.rules import GenericRule, RuleEffect, TargetType
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime


class CreateGenericRuleUseCase:
    def __init__(self, repository: RuleRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus

    async def execute(self, command: CreateGenericRuleCommand) -> UseCaseOutputDTO:
        try:
            rule = GenericRule(
                ruleEffect=_effect(command.ruleEffect),
                targetType=_target_type(command.targetType),
                rangeTime=_range(command.rangeTime),
                description=command.description,
                nome=command.nome,
            )
            await self._repository.save(rule)
            event = CreateGenericRuleEvent.from_entity(rule, triggered_by_id=command.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="generic_rule",
                resource_id=str(rule.id),
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_GENERIC_RULE_ERROR",
                message="Error creating generic rule",
                use_case=self.__class__.__name__,
                context={"command": str(command)},
                original=e,
            ) from e


def _effect(value: object) -> RuleEffect:
    return value if isinstance(value, RuleEffect) else RuleEffect[str(value).upper()]


def _target_type(value: object) -> TargetType:
    return value if isinstance(value, TargetType) else TargetType[str(value).upper()]


def _range(value: object) -> RangeTime:
    if isinstance(value, RangeTime):
        return value
    if isinstance(value, dict):
        return RangeTime(str(value["start_time"]), str(value["end_time"]))
    start, end = str(value).split("-", 1)
    return RangeTime(start.strip(), end.strip())
