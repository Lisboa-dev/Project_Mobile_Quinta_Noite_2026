from src.modules.agenda.domain.rules.BaseRule import BaseRule
from src.modules.agenda.domain.rules.RuleEnum import RuleEffect
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime


class OptimizeRules:
    def __init__(self):
        self._rules: list[BaseRule] = []

    def removeRedundantRules(self, rules: list[BaseRule] | None = None) -> list[BaseRule]:
        rules = rules or []

        ordered_rules = sorted(
            rules or [],
            key=lambda rule: (
                getattr(rule, "ruleEffectPriority", 999),
                getattr(getattr(rule, "rangeTime", None), "start_time", None) or "",
            ),
        )

        fixed_rules: list[BaseRule] = []
        arrayAdd: list[BaseRule] = []
        arrayRemove: list[BaseRule] = []

        for rule in ordered_rules:
            if rule.ruleEffect == RuleEffect.ADD and rule.rangeTime is not None:
                self.merge_into(arrayAdd, rule)

            elif rule.ruleEffect == RuleEffect.REMOVE and rule.rangeTime is not None:
                self.merge_into(arrayRemove, rule)
            else:
                fixed_rules.append(rule)

        self._rules = fixed_rules + arrayAdd + arrayRemove
        return self._rules

    @staticmethod
    def merge_into(target: list[BaseRule], rule: BaseRule) -> None:
        if not target:
            target.append(rule)
            return

        last = target[-1]
        if last.rangeTime is None or rule.rangeTime is None:
            target.append(rule)
            return

        fused_range = RangeTime.fusion(last.rangeTime, rule.rangeTime)

        if fused_range:
            last.rangeTime = fused_range
        else:
            target.append(rule)

    @property
    def rules(self):
        return self._rules
