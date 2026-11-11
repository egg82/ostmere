"""Worlds whose saves were written mid-lump by the engine before lumps were paid by work (d3400d5), shared by the
test that loads them (test_old_lump_saves.py) and the script that recorded them (record_lump_saves.py). Public engine
names only, so the recorder runs on that older engine unchanged."""
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, Amount, AtLeast, CardDef, CardId, CardShare, Flow, LineKey, Mix, MixId,
    Modifier, ModifierKind, Outcome, PacingCurve, Rules, Save, SaveMix, SkillDef, SkillId, SourceId, StandingDef,
    StoreDef, StoreId, StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, WorkRef, decide, new_save,
)

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
WALK, CHOP = CardId("walk"), CardId("chop")
ONE = LineKey("one.line")
SPEED = (11_000, 10_333)
"""1.1x and 1.0333x on each card's work: no whole duration, so the old per-second lump rates rounded, and no whole work
speed (11_366.3 units a second), so the old rates, which rounded the speed in with the lump, differ from a lump paid
by the work speed rounded down."""


def rules() -> Rules:
    """walk: a long HANDS card making one item of y (a trigger waits on it). chop: a short card taking an item of x and
    making two of z a completion, beside a standing fire that burns z: a store with a flow and a lump on it."""
    cards = (CardDef(WALK, 16_560, outcome=Outcome(stores=(Amount(Y, Q),))),
             CardDef(CHOP, 7, inputs=(Amount(X, Q),), outcome=Outcome(stores=(Amount(Z, 2 * Q),))))
    return Rules(stores=(StoreDef(X, 10**6 * Q, 10**5 * Q), StoreDef(Y, 100 * Q), StoreDef(Z, 10**6 * Q, 50 * Q)),
                 skills=(SkillDef(SkillId("k")),), standing=(StandingDef(ActionId("fire"), costs=(Flow(Z, 1_300),)),),
                 curve=PacingCurve((10**15,)), cards=cards,
                 triggers=(TriggerDef(TriggerId("one"), AtLeast(StoreValue(Y), Q, Q), Outcome(lines=(ONE,))),))


def started(r: Rules, scenario: str) -> Save:
    """At time 0: the walk tapped (`tap`), or chop run by the mix at its whole share (`mix`)."""
    mods = tuple(Modifier(WorkRef(c), ModifierKind.MUL_BP, m, SourceId(f"speed_{c}_{i}"))
                 for c in (WALK, CHOP) for i, m in enumerate(SPEED))
    s = new_save(r, mods)
    if scenario == "tap":
        return decide(s, r, 0, TapCard(WALK))
    s = decide(s, r, 0, SaveMix(Mix(MixId("m"), (CardShare(CHOP, BP),))))
    return decide(s, r, 0, SwitchMix(MixId("m")))


SAVED_AT = {"tap": 5_000, "mix": 1_000}
"""When each recorded save was written: the walk is a third done, chop is many completions in."""
