"""DESIGN.txt, "Next's row": the queue is a row among the hands' rules. Rules above it outrank a ready queue entry, as
when it sits at the bottom; rules under it wait while a ready entry has the hands and pick up again after. A ready
entry takes the hands when the task under way ends. A head that cannot act is passed over as a row (the rules under it
run) but still blocks the entries behind it inside the queue.

The world, as the owner plays it: a cure rule (rest) above Next, a replenish rule under it that chops while the wood
store is low, and builds queued When ready that each take an item of wood."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, AfterTime, Amount, AtLeast, AtMost, CardCount, CardDef, CardId, CardShare, Flow,
    Mix, MixId, Order, OrderState, PacingCurve, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, SkillDef,
    SkillId, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, advance, decide, new_save, validate_rules, view,
)
from ashfall_app.engine.codec import decode, encode

WOOD, FOOD = StoreId("wood"), StoreId("food")
CHOP, REST, BUILD, SHED, POKE = (CardId(n) for n in ("chop", "rest", "build", "shed", "poke"))
CHOPPING, RESTING = MixId("chopping"), MixId("resting")
REPLENISH = Order(AtMost(StoreValue(WOOD), 50 * Q, 60 * Q), SwitchMix(CHOPPING))
"""Chops while wood is at or under 50 items: on from the start (wood starts at 0), one item every 100 s."""


def world(max_firings: int = 1000) -> Rules:
    r = Rules(stores=(StoreDef(WOOD, 100 * Q), StoreDef(FOOD, 100 * Q)), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), max_firings_per_instant=max_firings,
              cards=(CardDef(CHOP, 100, makes=(Flow(WOOD, 36_000),)), CardDef(REST, 100, makes=(Flow(FOOD, 36_000),)),
                     CardDef(BUILD, 100, cap=1, inputs=(Amount(WOOD, Q),)), CardDef(SHED, 100, cap=1),
                     CardDef(POKE, 90, cap=1)))
    validate_rules(r)
    return r


def planned(r: Rules, orders: tuple[Order, ...], *queue: CardId) -> Save:
    """Both mixes saved, `orders` set and each of `queue` queued When ready (a tap until its one completion), at 0."""
    s = new_save(r)
    for mix, card in ((CHOPPING, CHOP), (RESTING, REST)):
        s = decide(s, r, 0, SaveMix(Mix(mix, (CardShare(card, BP),))))
    s = decide(s, r, 0, SetOrders(orders))
    return decide(s, r, 0, SetQueue(tuple(QueueEntry(TapCard(c), AtLeast(CardCount(c), 1, 1)) for c in queue)))


def under_next(order: Order) -> Order:
    return Order(order.when, order.then, order.unless, order.or_else, below_next=True)


def hands(s: Save) -> CardId | None:
    return next(ls.card for ls in s.lanes if ls.lane == HANDS)


def test_at_the_bottom_a_ready_entry_waits_while_a_rule_runs():
    """Today's behaviour, kept for every old save: BUILD is ready at 100 (an item of wood), but the replenish rule's mix
    runs, so the queue waits until it lets go."""
    r = world()
    s = planned(r, (REPLENISH,), BUILD)
    for t in (100, 150, 1000):
        a = advance(s, r, t)
        assert hands(a) is None and view(a, r).running_mix == CHOPPING and len(a.queue) == 1


def test_under_next_a_rule_runs_until_the_entry_is_ready_then_waits_and_resumes():
    """The owner's case (1) and (2): before BUILD is ready Next holds nothing and the replenish rule chops; at 100 BUILD
    takes the hands, the rule waits (named as behind Next), and once BUILD lands at 200 and leaves the queue, chopping
    resumes."""
    r = world()
    s = planned(r, (under_next(REPLENISH),), BUILD)
    early = advance(s, r, 50)
    assert hands(early) is None and view(early, r).running_mix == CHOPPING
    assert view(early, r).order_states == (OrderState.ON,)
    mid = advance(s, r, 150)
    assert hands(mid) == BUILD and view(mid, r).order_states == (OrderState.BEHIND_NEXT,)
    after = advance(s, r, 250)
    assert after.queue == () and hands(after) is None and view(after, r).running_mix == CHOPPING
    assert view(after, r).order_states == (OrderState.ON,)


def test_a_ready_entry_takes_the_hands_when_the_task_under_way_ends():
    """SHED, ready but for the hands, is queued at 10 while the player's tap of POKE (90 s, from 0) runs: SHED waits
    for POKE to land at 90 and starts then, never cutting in."""
    r = world()
    s = decide(planned(r, (under_next(REPLENISH),)), r, 0, TapCard(POKE))
    s = decide(s, r, 10, SetQueue((QueueEntry(TapCard(SHED), AtLeast(CardCount(SHED), 1, 1)),)))
    assert hands(s) == POKE and hands(advance(s, r, 89)) == POKE
    assert hands(advance(s, r, 90)) == SHED


def test_a_rule_above_next_still_wins():
    """The owner's case (3): the cure rule above Next runs its mix from 50; SHED, queued at 60 and ready, waits behind
    it, and the replenish rule under Next is outranked by the cure rule, not by Next."""
    r = world()
    cure = Order(AfterTime(50), SwitchMix(RESTING))
    s = planned(r, (cure, under_next(REPLENISH)))
    assert view(advance(s, r, 49), r).running_mix == CHOPPING
    s = decide(s, r, 60, SetQueue((QueueEntry(TapCard(SHED), AtLeast(CardCount(SHED), 1, 1)),)))
    a = advance(s, r, 150)
    assert hands(a) is None and view(a, r).running_mix == RESTING and len(a.queue) == 1
    assert view(a, r).order_states == (OrderState.ON, OrderState.OUTRANKED)


def test_a_head_that_cannot_act_is_passed_over_as_a_row_and_blocks_the_queue():
    """BUILD heads the queue and needs wood; SHED behind it is ready from the start. As a row, Next is passed over while
    BUILD cannot act, so the replenish rule chops; inside the queue BUILD is never passed over, so SHED waits too, until
    BUILD has taken its turn."""
    r = world()
    s = planned(r, (under_next(REPLENISH),), BUILD, SHED)
    a = advance(s, r, 50)
    assert hands(a) is None and view(a, r).running_mix == CHOPPING and len(a.queue) == 2
    assert hands(advance(s, r, 150)) == BUILD
    assert hands(advance(s, r, 250)) == SHED


@pytest.mark.parametrize("below", [False, True])
def test_a_goal_stint_runs_over_a_rule_under_next(below: bool):
    """A goal stint (run resting until an item of food, at 100) runs over the replenish rule only when the rule is under
    Next; above it, the rule's chopping runs and the stint waits. Under Next, chopping comes back when the stint pops."""
    r = world()
    s = planned(r, (under_next(REPLENISH) if below else REPLENISH,))
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(RESTING), AtLeast(StoreValue(FOOD), Q, Q)),)))
    a = advance(s, r, 50)
    assert view(a, r).running_mix == (RESTING if below else CHOPPING)
    assert view(a, r).order_states == ((OrderState.BEHIND_NEXT,) if below else (OrderState.ON,))
    if below:
        after = advance(s, r, 100)
        assert after.queue == () and view(after, r).running_mix == CHOPPING


def test_a_tap_rule_under_next_acts_while_the_head_cannot():
    """A rule under Next that taps CHOP on the hands while wood is low: BUILD at the head needs wood, so Next is passed
    over and the rule's tap starts at once; at its landing (100, an item of wood) BUILD is ready and takes the hands
    ahead of the rule, which taps again after BUILD lands at 200. The rule is set after the queue, so its tap is what
    that evaluation finds once Next is passed over."""
    r = world()
    s = decide(planned(r, (), BUILD), r, 0, SetOrders((under_next(Order(REPLENISH.when, TapCard(CHOP))),)))
    assert hands(s) == CHOP
    assert hands(advance(s, r, 100)) == BUILD and view(advance(s, r, 150), r).order_states == (OrderState.BEHIND_NEXT,)
    assert hands(advance(s, r, 200)) == CHOP


@pytest.mark.parametrize("max_firings, cascades", [(1000, 0), (2, 1)])
def test_the_rule_and_the_queue_trading_the_hands_makes_no_cascade(max_firings: int, cascades: int):
    """At 200 BUILD lands (a firing), pops, and SHED, ready, takes the hands (a firing) over the replenish rule, whose
    mix came back for no time at all: the instant ends well under a real cap. The cap of 2 is the control that the
    count sees a cascade at that instant."""
    r = world(max_firings)
    s = planned(r, (under_next(REPLENISH),), BUILD, SHED)
    a = advance(s, r, 200)
    assert a.cascade_count - advance(s, r, 199).cascade_count == cascades
    if cascades == 0:
        assert hands(a) == SHED and view(a, r).order_states == (OrderState.BEHIND_NEXT,)


def test_set_orders_keeps_next_one_row():
    """A rule set after one under Next lands under it too (an appended rule is the lowest priority), and moving a rule
    past Next keeps its latch: "wood at 0, until over an item" is still on at 50 with half an item, which a fresh latch
    would read as off."""
    r = world()
    low = Order(AtMost(StoreValue(WOOD), 0, Q), SwitchMix(CHOPPING))
    s = advance(planned(r, (low, under_next(Order(AfterTime(0), SwitchMix(RESTING))))), r, 50)
    a = decide(s, r, 50, SetOrders((*s.orders, Order(AtLeast(StoreValue(FOOD), Q, Q), SwitchMix(RESTING)))))
    assert [o.below_next for o in a.orders] == [False, True, True]
    assert s.latches[0] is True
    moved = decide(s, r, 50, SetOrders((under_next(low), s.orders[1])))
    assert moved.latches == s.latches and [o.below_next for o in moved.orders] == [True, True]


def test_the_row_is_saved_and_a_save_with_it_at_the_bottom_writes_nothing_new():
    """A save whose rules all sit above Next encodes as saves did before the row existed; one with a rule under it
    carries that through encode and decode."""
    r = world()
    s = planned(r, (REPLENISH,))
    assert "below_next" not in encode(s, r)
    moved = decide(s, r, 0, SetOrders((under_next(REPLENISH),)))
    assert decode(encode(moved, r), r).orders[0].below_next is True
