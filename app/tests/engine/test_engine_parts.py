"""The engine's leaf functions: units, segments, the rate formula, mix flattening, curve, rule validation, purity."""
import ast
import sys
from pathlib import Path
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, CardDef, CardId, CardShare, Flow, FlowKind, InvalidRulesError, InvalidVerbError, Mix, MixId, Modifier,
    ModifierKind, PacingCurve, RateRef, Rules, Run, RunKind, Segment, SkillDef, SkillId, SourceId, StoreDef, StoreId,
    SubMix, TimeOrderError, ceil_div, flatten_shares, level_for, modified_rate, reach_time, units, validate_rules,
    value_at, xp_for,
)

ENGINE = Path(__file__).resolve().parents[2] / "ashfall_app" / "engine"


def test_ceil_div_is_exact_for_both_signs():
    assert [ceil_div(7, 2), ceil_div(-7, 2), ceil_div(6, 3), ceil_div(0, 5)] == [4, -3, 2, 0]
    with pytest.raises(ValueError):
        ceil_div(1, 0)


def test_value_at_clamps_only_at_the_limit():
    seg = Segment(10, 100, -7, 0)
    assert value_at(seg, 10) == 100
    assert value_at(seg, 24) == 2
    assert value_at(seg, 25) == 0  # 100 - 105 overshoots; clamped
    assert value_at(Segment(0, 5, -1), 10) == -5  # no limit, no clamp
    with pytest.raises(TimeOrderError):
        value_at(seg, 9)


def test_reach_time_uses_ceiling_division_and_respects_limits():
    seg = Segment(10, 100, -7, 0)
    assert reach_time(seg, 0) == 10 + 15  # ceil(100 / 7)
    assert reach_time(seg, 100) == 10
    assert reach_time(seg, 101) is None  # wrong direction
    assert reach_time(Segment(0, 0, 3, 10), 11) is None  # past the limit
    assert reach_time(Segment(0, 0, 0), 1) is None


def test_modified_rate_sums_adds_then_compounds_multipliers():
    ref = RateRef(CardId("a"), FlowKind.MAKE, StoreId("s"))
    other = RateRef(CardId("b"), FlowKind.MAKE, StoreId("s"))
    stack = (
        Modifier(ref, ModifierKind.ADD_BP, 500, SourceId("x")),
        Modifier(ref, ModifierKind.MUL_BP, 15_000, SourceId("y")),
        Modifier(ref, ModifierKind.ADD_BP, 500, SourceId("z")),
        Modifier(other, ModifierKind.MUL_BP, 0, SourceId("ignored")),
    )
    e = modified_rate(ref, 4000, 5000, stack, Run(RunKind.FULL))
    assert e.per_hour == 3300  # 4000 * 0.5 * 1.10 * 1.5
    assert [m.source for m in e.adds] == ["x", "z"] and [m.source for m in e.muls] == ["y"]


def test_rounding_never_favours_the_player():
    make = RateRef(CardId("a"), FlowKind.MAKE, StoreId("s"))
    cost = RateRef(CardId("a"), FlowKind.COST, StoreId("s"))
    assert modified_rate(make, 1, 3333, (), Run(RunKind.FULL)).per_hour == 0
    assert modified_rate(cost, 1, 3333, (), Run(RunKind.FULL)).per_hour == 1
    neg = (Modifier(make, ModifierKind.ADD_BP, -20_000, SourceId("x")),)
    assert modified_rate(make, 1000, BP, neg, Run(RunKind.FULL)).per_hour == 0  # floored at 0, never negative


def test_flatten_shares_is_compositional_and_sums_repeats():
    a, b = CardId("a"), CardId("b")
    inner = Mix(MixId("inner"), (CardShare(a, 3333), CardShare(b, 6667)))
    outer = Mix(MixId("outer"), (CardShare(b, 2000), SubMix(MixId("inner"), 5000)))
    assert flatten_shares((inner, outer), MixId("outer")) == (CardShare(b, 2000 + 3333), CardShare(a, 1666))
    twice = Mix(MixId("twice"), (CardShare(a, 3333), CardShare(a, 3333)))
    wrap = Mix(MixId("wrap"), (SubMix(MixId("twice"), 5000),))
    assert flatten_shares((twice, wrap), MixId("wrap")) == (CardShare(a, 3333),)  # floor(6666 * 0.5), not 1666 * 2
    deep = (
        Mix(MixId("m0"), (CardShare(a, 3333), CardShare(b, 1000))),
        Mix(MixId("m1"), (SubMix(MixId("m0"), 5000), CardShare(b, 2000))),
        Mix(MixId("m2"), (SubMix(MixId("m1"), 3333), CardShare(a, 7))),
    )
    # m1 flattens to a 1666, b 500 + 2000; m2 scales that once: a 555 + 7, b 833
    assert flatten_shares(deep, MixId("m2")) == (CardShare(a, 562), CardShare(b, 833))
    loop = Mix(MixId("loop"), (SubMix(MixId("loop"), 100),))
    with pytest.raises(InvalidVerbError):
        flatten_shares((loop,), MixId("loop"))
    with pytest.raises(InvalidVerbError):
        flatten_shares((), MixId("missing"))


def test_curve_levels():
    curve = PacingCurve((100, 300))
    assert [level_for(curve, x) for x in (0, 99, 100, 299, 300, 10**9)] == [1, 1, 2, 2, 3, 3]
    assert [xp_for(curve, n) for n in (1, 2, 3)] == [0, 100, 300]
    with pytest.raises(ValueError):
        xp_for(curve, 4)


def _rules(**over: object) -> Rules:
    base = Rules(
        stores=(StoreDef(StoreId("s"), units(10)),),
        skills=(SkillDef(SkillId("k")),),
        standing=(),
        cards=(CardDef(CardId("a"), 60, skill=SkillId("k"), xp_per_hour=1, makes=(Flow(StoreId("s"), 1),)),),
        curve=PacingCurve((100,)),
    )
    return replace(base, **over)


@pytest.mark.parametrize("over", [
    {"stores": (StoreDef(StoreId("s"), 0),)},
    {"stores": (StoreDef(StoreId("s"), 10, 11),)},
    {"stores": (StoreDef(StoreId("s"), 10), StoreDef(StoreId("s"), 10))},
    {"cards": (CardDef(CardId("a"), 60, skill=SkillId("nope"), xp_per_hour=1),)},
    {"cards": (CardDef(CardId("a"), 60, skill=SkillId("k"), xp_per_hour=1, makes=(Flow(StoreId("x"), 1),)),)},
    {"cards": (CardDef(CardId("a"), 60, skill=SkillId("k"), xp_per_hour=1, makes=(Flow(StoreId("s"), 1),),
                       costs=(Flow(StoreId("s"), 1),)),)},
    {"curve": PacingCurve((100, 100))},
    {"curve": PacingCurve(())},
    {"max_firings_per_instant": 0},
])
def test_validate_rules_rejects(over: dict[str, object]):
    with pytest.raises(InvalidRulesError):
        validate_rules(_rules(**over))


def test_validate_rules_accepts_a_valid_set():
    validate_rules(_rules())


def test_engine_imports_only_stdlib_and_itself():
    files = sorted(ENGINE.glob("*.py"))
    assert len(files) > 5, "the purity test sees no engine files"
    bad: list[str] = []
    for f in files:
        for node in ast.walk(ast.parse(f.read_text())):
            if isinstance(node, ast.Import):
                bad += [f"{f.name}:{a.name}" for a in node.names if a.name.split(".")[0] not in sys.stdlib_module_names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                if (node.module or "").split(".")[0] not in sys.stdlib_module_names:
                    bad.append(f"{f.name}:{node.module}")
    assert not bad, bad
