"""What is pending now is read off the values now (engine schedule.py, pending): a pause's resume, a chip's or a rule's
latch change, and a requires turning are due now only when the values already say so, since every segment starts at
save.time and reaching a value from short of it takes a second at least. An instant asks after every handler, of saves
nothing else reads, so solving the stores' motion there was much of an instant's cost (issue 400)."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, AtLeast, AtMost, CardDef, CardId, CardShare, ChipDef, ChipId, Flow, Mix, MixId,
    Order, PacingCurve, Rules, Save, SaveMix, SetOrders, SkillDef, SkillId, StandingDef, StoreDef, StoreId,
    StoreValue, SwitchMix, advance, decide, new_save, per_hour, validate_rules,
)
from ashfall_app.engine import motion
from ashfall_app.engine.lumps import Terms
from ashfall_app.engine.schedule import events, pending

X, Y = StoreId("x"), StoreId("y")
EAT = ActionId("eat")
CHOP, DIG = CardId("chop"), CardId("dig")


def world() -> tuple[Rules, Save]:
    """x is eaten dry by a standing action and refilled by nothing (its eater paused from 3,600 s); y fills under chop
    and empties under dig; a rule switches to dig while y is at 5 items or more, and a chip shows while y is under 2."""
    r = Rules(stores=(StoreDef(X, 100 * Q, Q), StoreDef(Y, 100 * Q)), skills=(SkillDef(SkillId("k")),),
              standing=(StandingDef(EAT, (), (Flow(X, per_hour(1)),)),), curve=PacingCurve((10**15,)),
              cards=(CardDef(CHOP, 60, makes=(Flow(Y, per_hour(1)),)), CardDef(DIG, 60, costs=(Flow(Y, per_hour(1)),))),
              chips=(ChipDef(ChipId("low"), AtMost(StoreValue(Y), 2 * Q, 3 * Q)),))
    validate_rules(r)
    s = new_save(r)
    for m, c in ((MixId("a"), CHOP), (MixId("b"), DIG)):
        s = decide(s, r, 0, SaveMix(Mix(m, (CardShare(c, 10_000),))))
    s = decide(s, r, 0, SwitchMix(MixId("a")))
    return r, decide(s, r, 0, SetOrders((Order(AtLeast(StoreValue(Y), 5 * Q, 3 * Q), SwitchMix(MixId("b"))),)))


@pytest.mark.parametrize("t", [3600, 7200, 18_000, 18_001, 25_200, 32_400])
def test_pending_solves_no_store_motion_and_matches_events(t: int, monkeypatch: pytest.MonkeyPatch):
    r, s = world()
    s = advance(s, r, t)
    fresh = replace(s)   # a save object no memo has seen, as a handler's is
    built: list[int] = []
    real = motion.lump_terms   # what store_segment reads first when it solves a save's motion

    def counted(save: Save, rules: Rules) -> dict[StoreId, Terms]:
        built.append(save.time)
        return real(save, rules)

    monkeypatch.setattr(motion, "lump_terms", counted)
    now = pending(fresh, r)
    assert built == []
    monkeypatch.undo()
    assert now == [e for e in events(replace(s), r) if e.time == t]
