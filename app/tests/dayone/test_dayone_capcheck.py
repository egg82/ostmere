"""The cap-loss readout (capcheck.py) on fixture rules: a store at its cap that nothing draws shows its loss, the same
store with the trip in the mix shows none, and a readout that sampled no gathered store fails."""
import pytest

from ashfall_app.engine import (
    BP, Amount, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, Rules, Save, SaveMix, SkillDef, SkillId,
    StoreDef, StoreId, SwitchMix, decide, new_save,
)
from tests.dayone import capcheck

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


def test_a_full_store_nothing_draws_loses_most_of_its_making_at_both_absences():
    rules, save = world(mixed=False)
    found = capcheck.losses(save, rules)
    assert {h: found[h]["wood"].share > 0.5 for h in capcheck.HOURS} == {8: True, 24: True}
    assert capcheck.lines(save, rules)[0].startswith("  cap loss at the end, away 8 h: wood ")


def test_the_same_store_with_the_trip_in_the_mix_loses_nothing():
    rules, save = world(mixed=True)
    assert [x.lost for found in capcheck.losses(save, rules).values() for x in found.values()] == [0] * 4
    assert capcheck.lines(save, rules) == ["  cap loss at the end, away 8 h: none", "  cap loss at the end, away 24 h: none"]


def test_a_full_store_nothing_takes_still_shows_its_loss():
    rules, save = world(mixed=False, takes=False)
    assert capcheck.losses(save, rules)[8]["wood"].share > 0.5


def test_a_store_apart_is_not_gathered():
    rules, save = world(mixed=False, takes=False)
    with pytest.raises(AssertionError, match="no gathered store was sampled"):
        capcheck.lines(save, rules, ("wood",))


def test_a_store_no_card_makes_is_not_gathered():
    rules, _ = world(mixed=True)
    assert capcheck.gathered(rules) == {"wood", "found"}
