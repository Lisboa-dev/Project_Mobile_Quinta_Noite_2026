from src.modules.agenda.domain.rules import GenericRule, RuleEffect, TargetType
from src.modules.agenda.domain.valueObjects import Date, DayStatus, RangeTime


def calendar_days():
    return [
        {
            "rooms": [],
            "date": Date(day=1, month=6, year=2026),
            "weekday": 1,
            "availability": True,
            "status": DayStatus.AVAILABLE,
            "rules": [],
        },
        {
            "rooms": [],
            "date": Date(day=2, month=6, year=2026),
            "weekday": 2,
            "availability": True,
            "status": DayStatus.AVAILABLE,
            "rules": [],
        },
    ]


def base_day_rules():
    return [
        GenericRule(
            ruleEffect=RuleEffect.ADD,
            targetType=TargetType.DAY,
            rangeTime=RangeTime("08:00", "12:00"),
            description="mock morning schedule",
            nome="mock-day-rule",
        )
    ]
