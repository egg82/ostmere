"""A running-mix change re-decides only the pauses it can move (engine design/, "Running dry"): those on a store a
card of the old or the new running mix makes or costs. A pause on any other store stands until its RESUME, so a store
held empty for good is not re-paused, and its consumers rebuilt, at every mix change (issue 400)."""
import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, Rules, Save, SaveMix,
    SkillDef, SkillId, StandingDef, StoreDef, StoreId, SwitchMix, advance, decide, new_save, per_hour, segment,
    validate_rules,
)
from ashfall_app.engine import handlers, mixpauses

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
EAT, FILL = ActionId("eat"), ActionId("fill")
CHOP, DIG = CardId("chop"), CardId("dig")


def world(fill: int) -> tuple[Rules, Save]:
    """x starts at one item and is eaten by a standing action at one an hour, refilled by another at `fill` an hour;
    two mixes run cards that never touch x. With nothing refilling it, the eater pauses at 3,600 s."""
    standing = (StandingDef(EAT, (), (Flow(X, per_hour(1)),)),
                *((StandingDef(FILL, (Flow(X, fill),), ()),) if fill else ()))
    cards = (CardDef(CHOP, 60, makes=(Flow(Y, per_hour(1)),)), CardDef(DIG, 60, makes=(Flow(Z, per_hour(1)),)))
    r = Rules(stores=(StoreDef(X, 100 * Q, Q), StoreDef(Y, 100 * Q), StoreDef(Z, 100 * Q)),
              skills=(SkillDef(SkillId("k")),), standing=standing, curve=PacingCurve((10**15,)), cards=cards)
    validate_rules(r)
    s = new_save(r)
    for m, c in ((MixId("a"), CHOP), (MixId("b"), DIG)):
        s = decide(s, r, 0, SaveMix(Mix(m, (CardShare(c, 10_000),))))
    return r, decide(s, r, 0, SwitchMix(MixId("a")))


def test_a_mix_change_leaves_a_refilling_store_s_pause_until_its_resume():
    """x refills at a quarter of the eater's cost, so it empties at 4,800 s and an hour of the eater's cost is back at
    19,200 s. A switch at 7,200 s, with x a sixth refilled, leaves the eater paused; it resumes at 19,200 s and not
    before."""
    r, s = world(per_hour(1) // 4)
    s = decide(advance(s, r, 7200), r, 7200, SwitchMix(MixId("b")))
    assert [p.runner for p in s.pauses] == [EAT]
    assert segment(s, r, X).rate == per_hour(1) // 4
    assert [p.runner for p in advance(s, r, 19_199).pauses] == [EAT]
    assert advance(s, r, 19_200).pauses == ()


def test_a_mix_change_rebuilds_once_with_a_store_held_empty_for_good(monkeypatch: pytest.MonkeyPatch):
    """Nothing refills x: the switch keeps the eater's pause, so the dry rule has nothing to do at that instant."""
    r, s = world(0)
    s = advance(s, r, 7200)
    calls: list[str] = []
    real = mixpauses.rebuild

    def counted(save: Save, rules: Rules) -> Save:
        calls.append(str(save.time))
        return real(save, rules)

    for module in (mixpauses, handlers):
        monkeypatch.setattr(f"{module.__name__}.rebuild", counted)
    s = decide(s, r, 7200, SwitchMix(MixId("b")))
    assert [p.runner for p in s.pauses] == [EAT]
    assert calls == ["7200"]


def test_a_mix_change_clears_a_pause_on_a_store_its_cards_touch():
    """dig makes x in mix b: switching to b re-decides the eater's pause, as before, and x then rises."""
    r, _ = world(0)
    b = Mix(MixId("b"), (CardShare(DIG, 10_000),))
    r2 = Rules(stores=r.stores, skills=r.skills, standing=r.standing, curve=r.curve,
               cards=(r.cards[0], CardDef(DIG, 60, makes=(Flow(X, per_hour(2)),))))
    validate_rules(r2)
    s2 = decide(decide(new_save(r2), r2, 0, SaveMix(Mix(MixId("a"), (CardShare(CHOP, 10_000),)))), r2, 0, SaveMix(b))
    s2 = decide(advance(decide(s2, r2, 0, SwitchMix(MixId("a"))), r2, 7200), r2, 7200, SwitchMix(MixId("b")))
    assert s2.pauses == () and segment(s2, r2, X).rate == per_hour(1)
