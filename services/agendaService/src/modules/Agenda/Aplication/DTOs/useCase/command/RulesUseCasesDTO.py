from dataclasses import dataclass


@dataclass(frozen=True)
class CreateBlockRuleCommand:
    triggered_by_id: str | None = None
    date: object | None = None
    weekday: int | None = None
    description: str | None = None
    target: str | None = None
    targetType: object | None = None
    nome: str | None = None

@dataclass(frozen=True)
class CreateGenericRuleCommand:
    ruleEffect: object
    targetType: object
    rangeTime: object
    description: str
    triggered_by_id: str | None = None
    nome: str | None = None

@dataclass(frozen=True)
class CreateSpecificRuleCommand:
    ruleEffect: object
    target: str
    rangeTime: object
    description: str
    triggered_by_id: str | None = None
    nome: str | None = None

@dataclass(frozen=True)
class CreateSpecificDayRuleCommand:
    ruleEffect: object
    rangeTime: object
    description: str
    date: object
    triggered_by_id: str | None = None
    target: str | None = None
    targetType: object | None = None
    nome: str | None = None

@dataclass(frozen=True)
class CreateWeekRuleCommand:
    ruleEffect: object
    rangeTime: object
    description: str
    weekday: int
    triggered_by_id: str | None = None
    target: str | None = None
    targetType: object | None = None
    nome: str | None = None

@dataclass(frozen=True)
class DeleteRuleCommand:
    id: str
    triggered_by_id: str | None = None
