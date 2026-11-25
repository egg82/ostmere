"""Progress never needs the same tap repeated by hand (docs/decisions/pacing.md): the narrow hard check (tap_gates.py)
on the shipped opening, its controls, and its reach against the played routes. Heavy manual repetition anywhere else
is the readout's to report (report.py), never a failure here."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AtLeast, CardCount, CardId, Condition, Flow, Rules, SkillLevel, SkillId, StoreDef, StoreId, StoreValue,
    TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked,
)
from tests.opening.afterend import AfterEndPlayer
from tests.opening.playthrough import opening, opening_rules
from tests.opening.tap_gates import MANY_TAPS, reachable_before_automation, tap_heavy_gates

MIX = opening().first_mix.feature
AFTER_MIXES = AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, MIX)), 1, 1)
HOUR = 3_600_000


def test_no_story_gate_needs_many_taps_before_automation():
    assert tap_heavy_gates(opening_rules(), MIX) == []


def planted(when: Condition, requires: tuple[Condition, ...] = (), *, maker: str | None = None,
            per_tap: int = 0) -> Rules:
    """The shipped rules plus trigger t_planted; with `maker`, that card also makes planted_store, `per_tap` a
    completion (its own make flow, at its work_s)."""
    rules = opening_rules()
    store = StoreId("planted_store")
    cards = tuple(replace(c, makes=(*c.makes, Flow(store, per_tap * 3600 // c.work_s))) if c.id == maker else c
                  for c in rules.cards)
    trigger = TriggerDef(TriggerId("t_planted"), when, rules.triggers[0].outcome, requires)
    return replace(rules, cards=cards, stores=(*rules.stores, StoreDef(store, 100 * HOUR)),
                   triggers=(*rules.triggers, trigger))


def flagged(rules: Rules) -> list[str]:
    return [g for g in tap_heavy_gates(rules, MIX) if "t_planted" in g]


@pytest.mark.parametrize("count", [MANY_TAPS, 12])
def test_an_early_count_of_one_card_is_red(count: int):
    """The preview's kind of gate (12 gathers), planted where only hands can meet it."""
    assert flagged(planted(AtLeast(CardCount(CardId("gather_wood")), count, count))) == [
        f"trigger t_planted needs {count} taps of gather_wood before automation"]


def test_an_early_store_one_card_fills_is_red():
    rules = planted(AtLeast(StoreValue(StoreId("planted_store")), 12 * HOUR, 12 * HOUR), maker="scavenge", per_tap=HOUR)
    assert flagged(rules) == ["trigger t_planted needs 12 taps of scavenge before automation"]


def test_one_tap_short_of_many_is_green():
    assert flagged(planted(AtLeast(CardCount(CardId("gather_wood")), MANY_TAPS - 1, MANY_TAPS - 1))) == []


def test_a_store_threshold_after_automation_is_green():
    """The same store and amount as the red case, once mixes are open: the mix can fill it."""
    rules = planted(AtLeast(StoreValue(StoreId("planted_store")), 12 * HOUR, 12 * HOUR), (AFTER_MIXES,),
                    maker="scavenge", per_tap=HOUR)
    assert flagged(rules) == []


LEVEL = AtLeast(SkillLevel(SkillId("scavenging")), 12, 12)


def test_a_level_unlock_after_automation_is_green():
    assert flagged(planted(LEVEL, (AFTER_MIXES,))) == []


def test_a_level_unlock_before_automation_is_green():
    assert flagged(planted(LEVEL)) == []   # a level is never read as taps, before automation either


@pytest.mark.playthrough
def test_the_reach_holds_everything_a_route_has_when_mixes_open(typical: AfterEndPlayer, by_hand: AfterEndPlayer):
    """The check's 'before automation' misses nothing a played route had: its unlocks at the save where mixes open,
    less the mix feature itself."""
    reach = reachable_before_automation(opening_rules(), MIX)
    for p in (typical, by_hand):
        at = p.at(lambda q: q.has(UnlockKind.FEATURE, MIX))
        had = set(at.save.unlocked) - {Unlock(UnlockKind.FEATURE, MIX)}
        assert had and had <= reach
