"""The cap-loss check (capcheck.py) on fixture rules: a store at its cap that a card takes and nothing draws fails, the
same store with the trip in the mix passes, one nothing takes is reported and not failed, and a check that sampled no
gathered store fails."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, Amount, AtLeast, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, Rules, Save, SaveMix,
    SkillDef, SkillId, StoreDef, StoreId, StoreValue, SwitchMix, decide, new_save,
)
from tests.dayone import capcheck
from tests.dayone.wanted import wanted

WOOD, FOUND, STASH = StoreId("wood"), StoreId("found"), StoreId("stash")
RATE = 3600
HOUR = 3600
CAP = 4 * RATE * HOUR
MAKER, TRIP = CardId("maker"), CardId("trip")


def world(mixed: bool, takes: bool = True) -> tuple[Rules, Save]:
    """A maker into a full wood store. With `takes`, an uncapped trip takes wood faster than the maker makes it; with
    `mixed` too, production goes on the trip, which pauses when the wood runs dry and resumes once it is full again."""
    sk = SkillId("k0")
    cards = [CardDef(MAKER, 60, skill=sk, xp_per_hour=0, makes=(Flow(WOOD, 2 * RATE),))]
    shares = [CardShare(MAKER, BP // 2)]
    if takes:
        cards.append(CardDef(TRIP, 3600, inputs=(Amount(WOOD, 8 * RATE * HOUR),), makes=(Flow(FOUND, RATE),)))
    if mixed:
        shares.append(CardShare(TRIP, BP // 2))
    stores = (StoreDef(WOOD, CAP, CAP), StoreDef(FOUND, 10**9 * RATE * HOUR), StoreDef(STASH, CAP))
    rules = Rules(stores, (SkillDef(sk),), (), PacingCurve((10**15,)), 1000, cards=tuple(cards))
    mix = Mix(MixId("m0"), tuple(shares))
    return rules, decide(decide(new_save(rules), rules, 0, SaveMix(mix)), rules, 0, SwitchMix(mix.id))


def test_a_full_store_a_card_takes_that_nothing_draws_fails_at_both_absences():
    rules, save = world(mixed=False)
    found = capcheck.failing(save, rules)
    assert found == {"wood": (8, 24)}
    assert capcheck.problems(found) == ["wood loses over 50% of its making away 8 h and 24 h"]
    assert capcheck.unwanted(save, rules) == {}


def test_the_same_store_with_the_trip_in_the_mix_passes():
    rules, save = world(mixed=True)
    assert capcheck.failing(save, rules) == {}
    assert capcheck.unwanted(save, rules) == {}


def test_a_full_store_nothing_takes_is_reported_and_not_failed():
    rules, save = world(mixed=False, takes=False)
    assert capcheck.failing(save, rules) == {}
    assert capcheck.unwanted(save, rules) == {"wood": (8, 24)}


def test_a_store_a_condition_reads_is_wanted():
    rules, _ = world(mixed=False, takes=False)
    reader = CardDef(CardId("reader"), 60, requires=(AtLeast(StoreValue(WOOD), 1, 1),))
    assert wanted(rules) == set()
    assert wanted(replace(rules, cards=(*rules.cards, reader))) == {"wood"}


def test_a_store_apart_is_not_gathered():
    rules, save = world(mixed=False, takes=False)
    with pytest.raises(AssertionError, match="no gathered store was sampled"):
        capcheck.failing(save, rules, ("wood",))


def test_a_store_no_card_makes_is_not_gathered():
    rules, _ = world(mixed=True)
    assert capcheck.gathered(rules) == {"wood", "found"}
