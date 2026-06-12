from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime
from src.modules.agenda.domain.rules.RuleEnum import RuleEffect, TargetType
from src.modules.agenda.domain.rules.BaseRule import BaseRule


class WeekRule(BaseRule):
    
    def __init__(
        self,
        ruleEffect: RuleEffect,
        rangeTime: RangeTime,
        description: str,
        weekday: int,
        target: str | None = None,
        targetType: TargetType | None = None,
        nome: str | None = None
    ):
        super().__init__(
            ruleEffect=ruleEffect,
            target=target,
            rangeTime=rangeTime,
            description=description,
            weekday=weekday,
            targetType=targetType,
            nome=nome
        )
