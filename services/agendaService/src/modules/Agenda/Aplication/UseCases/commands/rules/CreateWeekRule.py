from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.command.RulesUseCasesDTO import CreateWeekRuleCommand
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RuleEvent import CreateWeekRuleEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import RuleRepositoryPort
from src.modules.agenda.domain.rules import RuleEffect, TargetType, WeekRule
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime


class CreateWeekRuleUseCase:
    def __init__(self, repository: RuleRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus

    async def execute(self, command: CreateWeekRuleCommand) -> UseCaseOutputDTO:
        try:
            rule = WeekRule(
                ruleEffect=_effect(command.ruleEffect),
                rangeTime=_range(command.rangeTime),
                description=command.description,
                weekday=command.weekday,
                target=command.target,
                targetType=_target_type(command.targetType),
                nome=command.nome,
            )
            await self._repository.save(rule)
            event = CreateWeekRuleEvent.from_entity(rule, triggered_by_id=command.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="week_rule",
                resource_id=str(rule.id),
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_WEEK_RULE_ERROR",
                message="Error creating week rule",
                use_case=self.__class__.__name__,
                context={"command": str(command), "original_error": str(e)},
                original=e,
            ) from e


def _effect(value: object) -> RuleEffect:
    if isinstance(value, RuleEffect):
        return value
    return RuleEffect[_effect_key(value)]


def _target_type(value: object) -> TargetType | None:
    if value is None or isinstance(value, TargetType):
        return value
    key = _enum_key(value)
    if key in {"", "NULL", "NONE"}:
        return None
    return TargetType[key]


def _range(value: object) -> RangeTime:
    if isinstance(value, RangeTime):
        return value
    if isinstance(value, dict):
        start = value.get("start_time") or value.get("start")
        end = value.get("end_time") or value.get("end")
        return RangeTime(str(start), str(end))
    start, end = str(value).split("-", 1)
    return RangeTime(start.strip(), end.strip())


def _enum_key(value: object) -> str:
    text = str(value).strip()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text.upper()


def _effect_key(value: object) -> str:
    aliases = {
        "ALLOW": "ADD",
        "AVAILABLE": "ADD",
        "DENY": "REMOVE",
        "DISALLOW": "REMOVE",
        "UNAVAILABLE": "REMOVE",
    }
    key = _enum_key(value)
    return aliases.get(key, key)
