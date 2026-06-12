
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime
from src.modules.agenda.domain.rules.RuleEnum import RuleEffect, TargetType
from src.modules.agenda.domain.rules.BaseRule import BaseRule
from src.modules.agenda.domain.valueObjects.Date import Date


class SpecificDayRule(BaseRule):
    
    def __init__(
        self,
        ruleEffect: RuleEffect,
        rangeTime: RangeTime,
        description: str,
        date: Date,
        target: str | None = None,
        targetType: TargetType | None = None,
        nome: str | None = None
    ):
        super().__init__(
            ruleEffect=ruleEffect,
            rangeTime=rangeTime,
            description=description,
            date=date,
            target=target,
            targetType=targetType,
            nome=nome
        )
