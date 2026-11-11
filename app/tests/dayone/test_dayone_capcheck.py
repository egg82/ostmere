"""The cap-loss check (capcheck.py) on fixture rules: a store at its cap that nothing draws fails, the same store with a
trip in the mix passes, and a check that sampled no gathered store fails."""
import pytest

from ashfall_app.engine import (
    BP, Amount, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, Rules, Save, SaveMix,
    SkillDef, SkillId, StoreDef, StoreId, SwitchMix, decide, new_save,
)
from tests.dayone import capcheck

WOOD, FOUND, STASH = StoreId("wood"), StoreId("found"), StoreId("stash")
RATE = 3600
HOUR = 3600
CAP = 4 * RATE * HOUR
MAKER, TRIP = CardId("maker"), CardId("trip")


def world(trip: bool) -> tuple[Rules, Save]:
    """A maker into a full wood store; with `trip`, an uncapped trip drawing wood faster than the maker makes it, so
    production goes on the trip, which pauses when the wood runs dry and resumes once it is full again."""
    sk = SkillId("k0")
    cards = [CardDef(MAKER, 60, skill=sk, xp_per_hour=0, makes=(Flow(WOOD, 2 * RATE),))]
    shares = [CardShare(MAKER, BP // 2)]
    if trip:
        cards.append(CardDef(TRIP, 3600, inputs=(Amount(WOOD, 8 * RATE * HOUR),), makes=(Flow(FOUND, RATE),)))
        shares.append(CardShare(TRIP, BP // 2))
    stores = (StoreDef(WOOD, CAP, CAP), StoreDef(FOUND, 10**9 * RATE * HOUR), StoreDef(STASH, CAP))
    rules = Rules(stores, (SkillDef(sk),), (), PacingCurve((10**15,)), 1000, cards=tuple(cards))
    mix = Mix(MixId("m0"), tuple(shares))
    return rules, decide(decide(new_save(rules), rules, 0, SaveMix(mix)), rules, 0, SwitchMix(mix.id))


def test_a_full_store_nothing_draws_fails_at_both_absences():
    rules, save = world(trip=False)
    found = capcheck.failing(save, rules)
    assert found == {"wood": (8, 24)}
    assert capcheck.problems(found) == ["wood loses over 50% of its making away 8 h and 24 h"]


def test_the_same_store_with_a_trip_in_the_mix_passes():
    rules, save = world(trip=True)
    assert capcheck.failing(save, rules) == {}


def test_a_store_apart_is_not_gathered():
    rules, save = world(trip=False)
    with pytest.raises(AssertionError, match="no gathered store was sampled"):
        capcheck.failing(save, rules, ("wood",))


def test_a_store_no_card_makes_is_not_gathered():
    rules, _ = world(trip=True)
    assert capcheck.gathered(rules) == {"wood", "found"}
