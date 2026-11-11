"""Lost to caps (caploss.py) on fixture rules: a maker into a full store loses exactly its rate times the span, a store
below its cap loses nothing, a history is summed between its decisions, and a measure that sampled nothing fails."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE, Amount, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, Rules, Save, SaveMix, SkillDef,
    Outcome, SkillId, StoreDef, StoreId, SwitchMix, advance, decide, new_save,
)
from tests.dayone import caploss

FULL, FILLING = StoreId("full"), StoreId("filling")
RATE = 3600
"""Each maker's rate once the mix halves it: the cards make twice this at full speed."""
CAP = 20 * QUANTITY_SCALE
HOUR = 3600


def world(rate: int = RATE) -> tuple[Rules, Save]:
    """A maker into a store that starts full and a maker into one that starts empty, each at half the mix."""
    sk = SkillId("k0")
    cards = tuple(CardDef(CardId(f"c{i}"), 60, skill=sk, xp_per_hour=0, makes=(Flow(s, 2 * rate),))
                  for i, s in enumerate((FULL, FILLING)))
    rules = Rules((StoreDef(FULL, CAP, CAP), StoreDef(FILLING, CAP, 0)), (SkillDef(sk),), (), PacingCurve((10**15,)),
                  1000, cards=cards)
    mix = Mix(MixId("m0"), tuple(CardShare(c.id, BP // 2) for c in cards))
    save = decide(decide(new_save(rules), rules, 0, SaveMix(mix)), rules, 0, SwitchMix(mix.id))
    return rules, save


def test_a_maker_into_a_full_store_loses_its_rate_times_the_span():
    rules, save = world()
    found = caploss.absences(save, rules, (2, 5))
    for h in (2, 5):
        assert found[h]["full"] == caploss.StoreLoss(made=RATE * h * HOUR, lost=RATE * h * HOUR)


def test_a_store_below_its_cap_loses_nothing_but_still_makes():
    rules, save = world()
    found = caploss.absences(save, rules, (2,))[2]["filling"]
    assert (found.made, found.lost) == (RATE * 2 * HOUR, 0)


def test_a_history_is_summed_between_its_decisions():
    rules, save = world()
    tally = caploss.Tally()
    caploss.between([save, advance(save, rules, HOUR), advance(save, rules, 3 * HOUR)], rules, tally)
    assert tally.losses()["full"].lost == RATE * 3 * HOUR


def test_a_measure_that_sampled_nothing_fails():
    rules, save = world()
    with pytest.raises(AssertionError, match="no store was sampled"):
        caploss.absences(save, rules, (0,))
    with pytest.raises(AssertionError, match="no store was sampled"):
        tally = caploss.Tally()
        caploss.between([save], rules, tally)
        tally.losses()


LUMP_S = 80
LUMP = 10 * QUANTITY_SCALE


def lump_world(start: int) -> tuple[Rules, Save]:
    """One card of LUMP_S seconds, capped at a single completion, landing LUMP into a store holding `start`: the lump
    lands as a rate over its 80 s, and the card stops when it completes."""
    sk, store = SkillId("k0"), StoreId("lump")
    card = CardDef(CardId("c0"), LUMP_S, skill=sk, xp_per_hour=0, outcome=Outcome(stores=(Amount(store, LUMP),)), cap=1)
    rules = Rules((StoreDef(store, CAP, start),), (SkillDef(sk),), (), PacingCurve((10**15,)), 1000, cards=(card,))
    mix = Mix(MixId("m0"), (CardShare(card.id, BP),))
    return rules, decide(decide(new_save(rules), rules, 0, SaveMix(mix)), rules, 0, SwitchMix(mix.id))


def test_a_short_lump_into_a_full_store_loses_the_lump_not_a_sample_step():
    """The planted overflow: all of the lump is dropped, so lost is the lump however long the span after it, where a
    fixed step held the lump's rate for the whole step."""
    rules, save = lump_world(CAP)
    found = caploss.absences(save, rules, (2,))[2]["lump"]
    assert found == caploss.StoreLoss(made=LUMP, lost=LUMP)


def test_a_lump_that_fills_a_store_loses_only_what_lands_past_the_cap():
    rules, save = lump_world(CAP - LUMP // 4)
    found = caploss.absences(save, rules, (2,))[2]["lump"]
    assert found == caploss.StoreLoss(made=LUMP, lost=LUMP * 3 // 4)


def test_a_lump_into_an_empty_store_loses_nothing():
    rules, save = lump_world(0)
    assert caploss.absences(save, rules, (2,))[2]["lump"].lost == 0
