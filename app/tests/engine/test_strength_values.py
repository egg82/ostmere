"""strengthmath.values_over against explain_over, the formula it reads in one pass: adds summed and floored at zero,
multipliers each divided out once, entries aimed at another strength or a rate left out."""
from ashfall_app.engine import (
    BP, CardId, FlowKind, Modifier, ModifierKind, PacingCurve, RateRef, Rules, SideId, SideStrength, SourceId, StoreId,
    Target, ThreatId, ThreatStrength,
)
from ashfall_app.engine.strengthdefs import SideDef, ThreatDef
from ashfall_app.engine.strengthmath import explain_over, values_over

HAND, WOLF, BEAR, IDLE = SideStrength(SideId("hand")), ThreatStrength(ThreatId("wolf")), ThreatStrength(
    ThreatId("bear")), SideStrength(SideId("idle"))
RULES = Rules((), (), (), PacingCurve((10**9,)), sides=(SideDef(SideId("hand"), 7), SideDef(SideId("idle"), 3)),
              threats=(ThreatDef(ThreatId("wolf"), 13), ThreatDef(ThreatId("bear"), 11)))


def m(target: Target, kind: ModifierKind, bp: int) -> Modifier:
    return Modifier(target, kind, bp, SourceId("s"))


def test_values_over_is_explain_over_for_every_target_in_one_pass():
    stack = (m(HAND, ModifierKind.ADD_BP, 2500), m(HAND, ModifierKind.MUL_BP, 15000), m(WOLF, ModifierKind.MUL_BP, 9000),
             m(HAND, ModifierKind.MUL_BP, 7000), m(WOLF, ModifierKind.ADD_BP, 3333), m(BEAR, ModifierKind.ADD_BP, -2 * BP),
             m(RateRef(CardId("x"), FlowKind.MAKE, StoreId("y")), ModifierKind.MUL_BP, 20000), m(IDLE, ModifierKind.ADD_BP, 999))
    targets = frozenset({HAND, WOLF, BEAR})
    got = values_over(stack, RULES, targets)
    assert got == {t: explain_over(stack, RULES, t).value for t in targets}
    assert got == {HAND: 7 * 12500 * 15000 * 7000 // BP ** 3, WOLF: 13 * 13333 * 9000 // BP ** 2, BEAR: 0}
