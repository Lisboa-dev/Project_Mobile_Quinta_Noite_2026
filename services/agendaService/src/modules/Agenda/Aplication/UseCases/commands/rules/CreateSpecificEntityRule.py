from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.command.RulesUseCasesDTO import CreateSpecificDayRuleCommand
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RuleEvent import CreateSpecificEntityRuleEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import RuleRepositoryPort
from src.modules.agenda.domain.rules import RuleEffect, SpecificDayRule, TargetType
from src.modules.agenda.domain.valueObjects import Date, RangeTime


class CreateSpecificDayRuleUseCase:
    def __init__(self, repository: RuleRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus

    async def execute(self, command: CreateSpecificDayRuleCommand) -> UseCaseOutputDTO:
        try:
            rule = SpecificDayRule(
                ruleEffect=_effect(command.ruleEffect),
                rangeTime=_range(command.rangeTime),
                description=command.description,
                date=_date(command.date),
                target=command.target,
                targetType=_target_type(command.targetType),
                nome=command.nome,
            )
            await self._repository.save(rule)
            event = CreateSpecificEntityRuleEvent.from_entity(rule, triggered_by_id=command.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="specific_day_rule",
                resource_id=str(rule.id),
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_SPECIFIC_ENTITY_RULE_ERROR",
                message="Error creating specific entity rule",
                use_case=self.__class__.__name__,
                context={"command": str(command)},
                original=e,
            ) from e


def _effect(value: object) -> RuleEffect:
    return value if isinstance(value, RuleEffect) else RuleEffect[str(value).upper()]


def _target_type(value: object) -> TargetType | None:
    if value is None or isinstance(value, TargetType):
        return value
    return TargetType[str(value).upper()]


def _range(value: object) -> RangeTime:
    if isinstance(value, RangeTime):
        return value
    if isinstance(value, dict):
        return RangeTime(str(value["start_time"]), str(value["end_time"]))
    start, end = str(value).split("-", 1)
    return RangeTime(start.strip(), end.strip())


def _date(value: object) -> Date:
    if isinstance(value, Date):
        return value
    if isinstance(value, dict):
        return Date(day=int(value["day"]), month=int(value["month"]), year=int(value["year"]))
    year, month, day = str(value).split("-")
    return Date(day=int(day), month=int(month), year=int(year))
