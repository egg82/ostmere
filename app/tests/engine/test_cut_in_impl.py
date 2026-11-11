"""DESIGN.txt, part "CUT-IN": a glowing step the player taps while the queue or a rule holds the hands takes them, the
held task keeps its work and is taken up again once the step lands; a hand tap and a step that does not glow are never
cut into."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, AtLeast, CardCount, CardDef, CardId, InvalidVerbError, Order, PacingCurve,
    QueueEntry, Rules, SetOrders, SetQueue, SkillDef, SkillId, StoreDef, StoreId, TapCard, advance, decide, new_save,
    validate_rules, view,
)
from ashfall_app.engine import Save

BUILD, STEP = CardId("build"), CardId("step")


def world(glows: bool = True) -> Rules:
    r = Rules(stores=(StoreDef(StoreId("x"), 100 * Q),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), cards=(CardDef(BUILD, 1000, cap=3), CardDef(STEP, 5, cap=1, glows=glows)))
    validate_rules(r)
    return r


def queued(r: Rules) -> Save:
    """The queue's one stage of BUILD on the hands from 0."""
    return decide(new_save(r), r, 0, SetQueue((QueueEntry(TapCard(BUILD), AtLeast(CardCount(BUILD), 1, 1)),)))


def cuts_in(r: Rules, s: Save) -> bool:
    return next(c.cuts_in for c in view(s, r).cards if c.card == STEP)


def work(s: Save, card: CardId) -> int:
    return next(cs.work.start_value for cs in s.cards if cs.card == card)


def test_a_glowing_step_cuts_in_on_the_queue_and_the_build_comes_back():
    r = world()
    s = advance(queued(r), r, 100)
    assert s.lanes[0].card == BUILD and cuts_in(r, s)
    s = decide(s, r, 100, TapCard(STEP))
    assert s.lanes[0].card == STEP and work(s, BUILD) == 100 * BP, "the build paused where it stood, its work kept"
    s = advance(s, r, 105)
    assert s.lanes[0].card == BUILD, "the step landed and the queue took the build up again"
    assert advance(s, r, 1005).lanes[0].card is None and work(advance(s, r, 1005), BUILD) == 1000 * BP


def test_a_glowing_step_cuts_in_on_a_rules_task():
    r = world()
    s = advance(decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(BUILD)),))), r, 50)
    assert s.lanes[0].card == BUILD and cuts_in(r, s)
    s = advance(decide(s, r, 50, TapCard(STEP)), r, 55)
    assert s.lanes[0].card == BUILD and work(s, BUILD) == 50 * BP


def test_a_hand_tap_is_never_cut_into():
    r = world()
    s = advance(decide(new_save(r), r, 0, TapCard(BUILD)), r, 100)
    assert not cuts_in(r, s)
    with pytest.raises(InvalidVerbError, match="busy"):
        decide(s, r, 100, TapCard(STEP))


def test_a_step_that_does_not_glow_waits_for_free_hands():
    r = world(glows=False)
    s = advance(queued(r), r, 100)
    assert not cuts_in(r, s)
    with pytest.raises(InvalidVerbError, match="busy"):
        decide(s, r, 100, TapCard(STEP))


def test_free_hands_need_no_cut_in():
    r = world()
    assert not cuts_in(r, new_save(r))
