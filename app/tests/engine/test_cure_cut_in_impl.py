"""DESIGN.txt, part "CURE CUT-IN": a cure for a chip shown now, tapped by the player, takes the hands from the task they
run; the task keeps its work, and one no order or queue entry taps goes to the queue's front, so it is taken up again
once the cure lands. An order's cure never cuts in (a drawn landing comes true while the player is away); a cure never
cuts into a cure, and with no chip shown a cure waits for free hands."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, Amount, AtLeast, AtMost, CardCount, CardDef, CardId, CardShare, ChipDef, ChipId,
    Flow, InvalidVerbError, Mix, MixId, Order, Outcome, PacingCurve, QueueEntry, Rules, Save, SaveMix, SetOrders,
    SetQueue, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, advance, decide,
    new_save, validate_rules, view,
)
from ashfall_app.engine.ids import ActionId

BUILD, EAT, SNACK = CardId("build"), CardId("eat"), CardId("snack")
FOOD = StoreId("food")
HUNGRY = AtMost(StoreValue(FOOD), 5 * Q, 8 * Q)
EATS = Order(HUNGRY, TapCard(EAT))


def world(food: int = 10 * Q) -> Rules:
    """FOOD drains five items in the first 100 s, so the chip shows at 100 while a 1000 s stage of BUILD runs; EAT and
    SNACK each put it back up past the chip's release."""
    fed = Outcome(stores=(Amount(FOOD, 5 * Q),))
    r = Rules(stores=(StoreDef(FOOD, 100 * Q, food),), skills=(SkillDef(SkillId("k")),),
              standing=(StandingDef(ActionId("body"), costs=(Flow(FOOD, 180_000),)),), curve=PacingCurve((10**9 * Q,)),
              cards=(CardDef(BUILD, 1000, cap=3), CardDef(EAT, 10, outcome=fed), CardDef(SNACK, 10, outcome=fed)),
              chips=(ChipDef(ChipId("hungry"), HUNGRY),))
    validate_rules(r)
    return r


def cuts_in(r: Rules, s: Save, card: CardId) -> bool:
    return next(c.cuts_in for c in view(s, r).cards if c.card == card)


def work(s: Save, card: CardId) -> int:
    return next(cs.work.start_value for cs in s.cards if cs.card == card)


def one_stage(n: int) -> QueueEntry:
    return QueueEntry(TapCard(BUILD), AtLeast(CardCount(BUILD), n, n))


def test_the_players_cure_cuts_in_on_a_hand_tap_and_the_task_comes_back():
    r = world()
    s = advance(decide(new_save(r), r, 0, TapCard(BUILD)), r, 100)
    assert s.chips == (True,) and cuts_in(r, s, EAT)
    s = decide(s, r, 100, TapCard(EAT))
    assert s.lanes[0].card == EAT and work(s, BUILD) == 100 * BP, "the build paused where it stood, its work kept"
    assert s.queue == (one_stage(1),), "the hand-tapped stage went to the queue's front"
    s = advance(s, r, 110)
    assert s.chips == (False,) and s.lanes[0].card == BUILD, "the cure landed and the queue took the build up again"
    s = advance(s, r, 1010)
    assert work(s, BUILD) == 1000 * BP and s.queue == () and s.lanes[0].card is None


WEAVE, WEAVING = CardId("weave"), MixId("weaving")
WATTLE = StoreId("wattle")


def woven_world() -> Rules:
    """world() plus a rule that runs a mix of WEAVE, which neither cures nor touches FOOD, while WATTLE is low: WEAVE
    adds one item an hour, so the rule stays true for the whole stage."""
    r = world()
    r = replace(r, stores=(*r.stores, StoreDef(WATTLE, 100 * Q, 0)),
                cards=(*r.cards, CardDef(WEAVE, 3600, outcome=Outcome(stores=(Amount(WATTLE, Q),)))))
    validate_rules(r)
    return r


def test_the_task_a_cure_cut_into_comes_back_while_a_rules_mix_runs():
    r = woven_world()
    s = decide(new_save(r), r, 0, SaveMix(Mix(WEAVING, (CardShare(WEAVE, 10_000),))))
    s = decide(s, r, 0, SetOrders((Order(AtMost(StoreValue(WATTLE), 50 * Q, 60 * Q), SwitchMix(WEAVING)),)))
    s = advance(decide(s, r, 0, TapCard(BUILD)), r, 100)
    assert s.lanes[0].card == BUILD and s.chips == (True,) and cuts_in(r, s, EAT)
    s = advance(decide(s, r, 100, TapCard(EAT)), r, 110)
    assert s.chips == (False,) and view(s, r).running_mix == WEAVING, "the cure landed under the rule's mix"
    assert s.lanes[0].card == BUILD and work(s, BUILD) == 100 * BP, "the build took the hands back from its kept work"
    assert advance(s, r, 1010).queue == ()


def test_the_players_cure_on_the_queues_task_leaves_it_to_the_queue():
    r = world()
    s = advance(decide(new_save(r), r, 0, SetQueue((one_stage(1),))), r, 100)
    s = decide(s, r, 100, TapCard(EAT))
    assert s.lanes[0].card == EAT and s.queue == (one_stage(1),), "queued once, by the player's own entry"
    assert advance(s, r, 110).lanes[0].card == BUILD


def test_the_players_cure_on_a_rules_task_leaves_it_to_the_rule():
    r = world()
    s = advance(decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(BUILD)),))), r, 100)
    s = decide(s, r, 100, TapCard(EAT))
    assert s.lanes[0].card == EAT and s.queue == (), "the rule takes it up again"
    s = advance(s, r, 110)
    assert s.lanes[0].card == BUILD and work(s, BUILD) == 100 * BP


def test_an_orders_cure_waits_for_the_stage_to_land():
    r = world()
    s = decide(decide(new_save(r), r, 0, SetOrders((EATS,))), r, 0, TapCard(BUILD))
    s = advance(s, r, 500)
    assert s.chips == (True,) and s.lanes[0].card == BUILD and work(s, BUILD) == 500 * BP
    assert advance(s, r, 1000).lanes[0].card == EAT


def test_a_cure_never_cuts_into_a_cure():
    r = world(food=4 * Q)
    s = decide(new_save(r), r, 0, TapCard(EAT))
    assert not cuts_in(r, s, SNACK)
    with pytest.raises(InvalidVerbError, match="busy"):
        decide(s, r, 0, TapCard(SNACK))


def test_with_no_chip_shown_a_cure_waits_for_free_hands():
    r = world(food=100 * Q)
    s = advance(decide(new_save(r), r, 0, TapCard(BUILD)), r, 100)
    assert s.chips == (False,) and not cuts_in(r, s, EAT)
    with pytest.raises(InvalidVerbError, match="busy"):
        decide(s, r, 100, TapCard(EAT))
