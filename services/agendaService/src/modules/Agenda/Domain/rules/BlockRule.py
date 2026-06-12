from src.modules.agenda.domain.valueObjects.Date import Date
from src.modules.agenda.domain.rules.RuleEnum import RuleEffect, TargetType
from src.modules.agenda.domain.rules.BaseRule import BaseRule


class BlockRule(BaseRule):
    
    def __init__(
        self,
        date: Date | None = None,
        weekday: int | None = None,
        description: str | None = None,
        target: str | None = None,
        targetType: TargetType | None = None,
        nome: str | None = None
    ):
        
        super().__init__(
            ruleEffect=RuleEffect.BLOCK,
            date=date,
            weekday=weekday,
            description=description,
            target=target,
            targetType=targetType,
            nome=nome
        )
           
        
    
