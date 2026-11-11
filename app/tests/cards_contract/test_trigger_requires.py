"""A trigger's requires (DESIGN.txt, "Triggers"): it fires at the first instant its condition and every requirement
hold, each requirement on an unlock or a runner; while one is false it waits, and fires at the instant that changes."""
import pytest

from ashfall_app.engine import (
    AtLeast, AtMost, CardDef, CardId, Flow, InvalidRulesError, LineKey, Outcome, Rules, Running, StandingDef, StoreDef,
    StoreId, StoreValue, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, ActionId, advance_logged,
    decide_logged, new_save, validate_rules,
)
from cards_world import Q, rules

A, B, R = CardId("a"), CardId("b"), CardId("r")
X = StoreId("x")
FA, FB = Unlock(UnlockKind.FEATURE, "fa"), Unlock(UnlockKind.FEATURE, "fb")
FIRED = LineKey("t.fired")
RISE = Unlock(UnlockKind.ACTION, "rise")
A_FIRST = (AtLeast(Unlocked(FA), 1, 1), AtMost(Unlocked(FB), 0, 0))
"""a built and b not: the order the player chose."""


def world(when: AtLeast | AtMost, requires: tuple[AtLeast | AtMost, ...] = A_FIRST) -> Rules:
    """a and b are one-off steps, each unlocking its feature; r is a step to read by; x rises by itself, an item a
    second."""
    return rules(
        [StoreDef(X, 100 * Q, 0)],
        cards=[CardDef(A, 10, cap=1, finished=Outcome(unlocks=(FA,))),
               CardDef(B, 10, cap=1, finished=Outcome(unlocks=(FB,))),
               CardDef(R, 10, cap=1)],
        standing=[StandingDef(ActionId("rise"), makes=(Flow(X, Q),))],
        triggers=[TriggerDef(TriggerId("t"), when, Outcome(lines=(FIRED,)), requires)],
        opening=[*(Unlock(UnlockKind.CARD, c) for c in (A, B, R)), Unlock(UnlockKind.STORE, X), RISE])


def fired_at(r: Rules, taps: list[tuple[int, CardId]], until: int) -> list[int]:
    s, times = new_save(r), list[int]()
    for t, card in taps:
        step = advance_logged(s, r, t)
        times += [ln.time for ln in step.lines if ln.key == FIRED]
        tapped = decide_logged(step.save, r, t, TapCard(card))
        times += [ln.time for ln in tapped.lines if ln.key == FIRED]
        s = tapped.save
    step = advance_logged(s, r, until)
    return times + [ln.time for ln in step.lines if ln.key == FIRED]


READING = AtLeast(Running(R), 1, 1)


def test_fires_when_the_card_starts_with_the_requirements_held():
    assert fired_at(world(READING), [(0, A), (20, R)], 100) == [20]


def test_never_fires_when_a_requirement_is_false_at_its_moment():
    assert fired_at(world(READING), [(0, B), (20, A), (40, R)], 100) == []


def test_waits_for_a_requirement_then_fires_at_the_instant_it_turns_true():
    """x holds from time 0; a's completion at 10 is the instant the requirement turns true."""
    assert fired_at(world(AtLeast(StoreValue(X), 0, 0)), [(0, A)], 100) == [10]


def test_a_continuous_condition_fires_at_its_solved_time_once_the_requirements_hold():
    """x reaches 30 at 30 s, an instant nothing else marks."""
    assert fired_at(world(AtLeast(StoreValue(X), 30 * Q, 30 * Q)), [(0, A)], 100) == [30]


def test_a_requirement_turned_false_at_the_same_instant_holds_it_back():
    """b completes at 20, the instant x reaches 20: the landing comes before the trigger (DESIGN.txt, "Same instant")."""
    assert fired_at(world(AtLeast(StoreValue(X), 20 * Q, 20 * Q)), [(0, A), (10, B)], 100) == []


def test_no_requirements_is_a_plain_trigger():
    assert fired_at(world(READING, ()), [(0, B), (20, R)], 100) == [20]


@pytest.mark.parametrize("bad", [AtLeast(StoreValue(X), Q, Q), AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, "nope")), 1, 1)])
def test_a_requirement_on_a_store_or_an_unknown_unlock_is_refused(bad: AtLeast):
    with pytest.raises(InvalidRulesError):
        validate_rules(world(READING, (bad,)))
