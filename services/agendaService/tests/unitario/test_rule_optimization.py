from src.infra.cache import OptimizeRules
from src.modules.agenda.domain.rules import BlockRule, GenericRule, RuleEffect, TargetType
from src.modules.agenda.domain.valueObjects import RangeTime


def test_optimize_rules_merges_contiguous_add_ranges():
    rules = [
        GenericRule(RuleEffect.ADD, TargetType.DAY, RangeTime("08:00", "10:00"), "a"),
        GenericRule(RuleEffect.ADD, TargetType.DAY, RangeTime("10:00", "12:00"), "b"),
    ]

    optimized = OptimizeRules().removeRedundantRules(rules)

    assert len(optimized) == 1
    assert str(optimized[0].rangeTime) == "08:00 - 12:00"


def test_optimize_rules_keeps_block_rules():
    block = BlockRule(weekday=0, description="holiday")
    rules = [
        block,
        GenericRule(RuleEffect.ADD, TargetType.DAY, RangeTime("08:00", "10:00"), "a"),
    ]

    optimized = OptimizeRules().removeRedundantRules(rules)

    assert block in optimized
