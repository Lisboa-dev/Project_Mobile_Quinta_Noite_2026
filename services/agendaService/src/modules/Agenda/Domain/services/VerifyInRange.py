from src.modules.agenda.domain.rules.RuleEnum import RuleEffect
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime



class VerifyInRange:
    
    @staticmethod
    def execute(time: RangeTime, rules: list) -> bool:
        
        ordered_rules = sorted(
            rules or [],
            key=lambda rule: (
                getattr(rule, "ruleEffectPriority", 999),
                getattr(getattr(rule, "rangeTime", None), "start_time", None) or "",
            ),
        )
        
        for r in ordered_rules:
           range_time = getattr(r, "rangeTime", None)
          
           if r.ruleEffect == RuleEffect.BLOCK:
                return False
               
           if range_time is not None and r.ruleEffect == RuleEffect.ADD and range_time.overlaps(time):
                   return True
               
           if range_time is not None and r.ruleEffect == RuleEffect.REMOVE and range_time.overlaps(time):
                   return False
                   
        return False
