from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from src.modules.agenda.domain.rules import BaseRule
from src.modules.agenda.aplication.events._helpers import enum_value, text, utc_now


@dataclass(frozen=True)
class RulePayload:
    triggered_by_id: str | None
    rule_id: str
    rule_effect: str
    range_start: str | None
    range_end: str | None
    description: str | None
    date: str | None
    weekday: int | None
    target: str | None
    target_type: str | None
    nome: str | None
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, rule: BaseRule, triggered_by_id: str | None):
        return cls(
            triggered_by_id=triggered_by_id,
            rule_id=str(rule.id),
            rule_effect=str(enum_value(rule.ruleEffect)),
            range_start=text(rule.startTime),
            range_end=text(rule.endTime),
            description=rule.description,
            date=text(rule.date),
            weekday=rule.weekday,
            target=rule.target,
            target_type=text(enum_value(rule.targetType)),
            nome=rule.nome,
        )


@dataclass(frozen=True)
class BlockRuleCreatedEvent(RulePayload):
    EVENT_NAME: ClassVar[str] = "agenda.rule.block.created"


@dataclass(frozen=True)
class GenericRuleCreatedEvent(RulePayload):
    EVENT_NAME: ClassVar[str] = "agenda.rule.generic.created"


@dataclass(frozen=True)
class SpecificDayRuleCreatedEvent(RulePayload):
    EVENT_NAME: ClassVar[str] = "agenda.rule.specific_day.created"


@dataclass(frozen=True)
class SpecificRuleCreatedEvent(RulePayload):
    EVENT_NAME: ClassVar[str] = "agenda.rule.specific.created"


@dataclass(frozen=True)
class WeekRuleCreatedEvent(RulePayload):
    EVENT_NAME: ClassVar[str] = "agenda.rule.week.created"


@dataclass(frozen=True)
class RuleDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.rule.deleted"

    triggered_by_id: str | None
    rule_id: str
    occurred_at: datetime = field(default_factory=utc_now)


CreateBlockRuleEvent = BlockRuleCreatedEvent
CreateGenericRuleEvent = GenericRuleCreatedEvent
CreateSpecificEntityRuleEvent = SpecificDayRuleCreatedEvent
CreateSpecificRuleEvent = SpecificRuleCreatedEvent
CreateWeekRuleEvent = WeekRuleCreatedEvent
DeleteRuleEvent = RuleDeletedEvent
