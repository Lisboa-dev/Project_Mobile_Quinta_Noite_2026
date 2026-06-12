
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime
from src.modules.agenda.domain.rules.RuleEnum import RuleEffect, TargetType
from src.modules.agenda.domain.rules.BaseRule import BaseRule


class SpecificRule(BaseRule):
    
    def __init__(
        self,
        ruleEffect: RuleEffect,
        rangeTime: RangeTime,
        description: str,
        id: str | None = None,
        type: TargetType | None = None,
        target: str | None = None,
        targetType: TargetType | None = None,
        nome: str | None = None,
        rule_id: str | None = None,
    ):
        super().__init__(
            ruleEffect=ruleEffect,
            id=rule_id,
            target=target if target is not None else id,
            targetType=targetType if targetType is not None else type,
            rangeTime=rangeTime,
            description=description,
            nome = nome
        )
