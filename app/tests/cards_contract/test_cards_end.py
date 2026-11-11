"""The end (DESIGN.txt, "The end", invariants 45-46): Save.ended_at is set at the first resolved instant where
rules.end is unlocked, never before, and once set it never changes; the view serves it;
it round-trips through the codec; rules naming an unknown end feature are invalid."""
from dataclasses import replace

import pytest
from hypothesis import given

from ashfall_app.engine import (
    AfterTime, AtMost, CardDef, CardId, FeatureId, Flow, InvalidRulesError, Order, Outcome, Amount, Rules, Save,
    SetOrders, StandingDef, StoreDef, StoreId, StoreValue, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind,
    ActionId, advance, decide, decode, encode, new_save, next_event, validate_rules, view,
)
from cards_gen import Scenario, few, scenario_st, span, try_decide
from cards_world import Q, rules

W = StoreId("w")
G = CardId("g")
FIRE = ActionId("fire")
END = FeatureId("end")
WOOD_RULE = SetOrders((Order(AtMost(StoreValue(W), 5 * Q, 8 * Q), TapCard(G)),))


def world(end: FeatureId | None = END, unlock_at: int = 100) -> Rules:
    """A fire burns wood at an item an hour, so the wood line falls; g gathers wood; a trigger unlocks the end feature
    at `unlock_at`. Gated: the feature is locked until then."""
    r = rules([StoreDef(W, 100 * Q, 10 * Q)],
              standing=[StandingDef(FIRE, costs=(Flow(W, 1000),))],
              cards=[CardDef(G, 100, outcome=Outcome(stores=(Amount(W, Q),)))],
              triggers=[TriggerDef(TriggerId("t_end"), AfterTime(unlock_at), Outcome(unlocks=(Unlock(UnlockKind.FEATURE, END),)))],
              opening=[Unlock(UnlockKind.STORE, W), Unlock(UnlockKind.CARD, G), Unlock(UnlockKind.ACTION, FIRE)])
    r = replace(r, end=end)
    validate_rules(r)
    return r


def holds(s: Save, r: Rules) -> bool:
    """The end's condition read off the view: the end feature unlocked."""
    return r.end is not None and Unlock(UnlockKind.FEATURE, r.end) in view(s, r).unlocked


def test_the_feature_is_the_end_while_a_line_falls_uncovered():
    """The feature unlocks at 100 while the wood line falls uncovered: the end is 100, and the view serves it."""
    r = world()
    s = advance(new_save(r), r, 99)
    assert s.ended_at is None and view(s, r).ended_at is None
    s = advance(s, r, 200)
    assert not view(s, r).all_covered and s.ended_at == 100 and view(s, r).ended_at == 100


def test_every_line_covered_before_the_feature_ends_at_the_feature_s_instant():
    """Covered from time 0, but the feature only unlocks at 100: the end is 100, not 0 and not a later sample."""
    r = world()
    s = decide(new_save(r), r, 0, WOOD_RULE)
    assert view(s, r).all_covered and s.ended_at is None
    assert advance(s, r, 99).ended_at is None
    assert advance(s, r, 100).ended_at == 100
    assert advance(s, r, 4321).ended_at == 100


def test_once_recorded_the_end_never_clears_nor_moves():
    """Invariant 46: after the end at 100, rules set and removed later leave ended_at at 100."""
    r = world()
    s = decide(advance(new_save(r), r, 200), r, 300, WOOD_RULE)
    s = decide(s, r, 400, SetOrders(()))
    assert s.ended_at == 100 and view(s, r).ended_at == 100


def test_rules_without_an_end_never_record_one():
    r = world(end=None)
    s = decide(advance(new_save(r), r, 200), r, 300, WOOD_RULE)
    assert s.ended_at is None


def test_ungated_rules_end_at_time_0():
    """With rules.opening None every feature counts as unlocked, so a save ends at 0."""
    r = replace(world(), opening=None)
    assert new_save(r).ended_at == 0


def test_an_unknown_end_feature_is_invalid():
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), end=FeatureId("nowhere")))


def test_the_end_round_trips_through_the_codec():
    r = world()
    s = advance(new_save(r), r, 200)
    assert s.ended_at == 100
    assert decode(encode(s, r), r) == s
    before = advance(new_save(r), r, 50)
    assert encode(before, r) != encode(replace(before, ended_at=40), r)


def _with_end(r: Rules, unlock_at: int) -> Rules:
    """A generated world given an end feature that a trigger unlocks at `unlock_at`."""
    trig = TriggerDef(TriggerId("t_end"), AfterTime(unlock_at), Outcome(unlocks=(Unlock(UnlockKind.FEATURE, END),)))
    out = replace(r, triggers=r.triggers + (trig,), end=END)
    validate_rules(out)
    return out


@few(8)
@given(sc=scenario_st())
def test_the_end_is_the_first_resolved_instant_the_condition_holds(sc: Scenario):
    """Invariants 45-46 over random worlds: walking every resolved instant (each event, each decision), ended_at is
    None while the condition has never held, becomes exactly the time of the first instant it holds, and never changes
    after. Splitting the time past the last step at each event, and a second before it, gives the same save (invariant
    1 with the end)."""
    r = _with_end(sc.rules, 500)
    s = new_save(r, sc.modifiers)
    seen: list[Save] = [s]
    for dt, verb in sc.steps:
        t = s.time + dt
        while (ne := next_event(s, r)) is not None and ne.time <= t:
            s = advance(s, r, ne.time)
            seen.append(s)
        s = try_decide(s, r, t, verb)
        seen.append(s)
    first: int | None = None
    for x in seen:
        if first is None and holds(x, r):
            first = x.time
        assert x.ended_at == first, (x.time, x.ended_at, first)
    end = s.time + span(r, 2000)
    direct = advance(s, r, end)
    t1 = s
    while (ne := next_event(t1, r)) is not None and ne.time <= end:
        t1 = advance(t1, r, ne.time)
        assert advance(t1, r, end) == direct, t1.time
        assert advance(advance(s, r, ne.time - 1), r, end) == direct, ne.time
