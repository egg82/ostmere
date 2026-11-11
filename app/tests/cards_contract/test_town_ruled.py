"""A lane run by rules (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Ruled lane", "The lane's
task", "The queue is the hands' plan", "Lane order"; invariants 58 and 63; api CONTRACT.txt, "A LANE RUN BY RULES").
The player never taps a ruled lane; orders and an Outcome's start drive it exactly as an unruled lane. Its task is its
first true rule whose card is ready, changed at its next landing. LaneBar.order names the rule whose task the lane
runs; a later true tap rule on that lane is OUTRANKED."""
import pytest

from ashfall_app.engine import (
    HANDS, AfterTime, AtLeast, AtMost, CardShare, InvalidVerbError, LaneBar, LaneId, Mix, MixId, Order, OrderState,
    Outcome, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, StoreValue, TapCard, TriggerDef, TriggerId,
    advance, decide, new_save, view,
)
from cards_world import Q, RACK, done
from town_world import H, NEVER, R, T1, T2, TC, TOWN, X, always, mixing, running, started, town, unruled

ON, WAITING, OUTRANKED, PASSED = OrderState.ON, OrderState.WAITING, OrderState.OUTRANKED, OrderState.PASSED_OVER
BIG = AtLeast(StoreValue(X), 90 * Q, 90 * Q)
"""A store rule that stays false in these runs."""


def bar(s: Save, r: Rules, lane: LaneId) -> LaneBar:
    found = [b for b in view(s, r).lanes if b.lane == lane]
    assert len(found) == 1, view(s, r).lanes
    return found[0]


# ---- the player's tap refused; every other tap as on any lane --------------------------------------------------

def test_a_players_tap_of_a_ruled_lane_card_is_refused_and_unruled_it_is_not():
    """Invariant 58, first half: the player's TapCard of t1 raises InvalidVerbError; with the lane unruled the same tap
    runs t1 (the control)."""
    r = town()
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, TapCard(T1))
    assert running(decide(new_save(unruled(r)), unruled(r), 0, TapCard(T1)), TOWN) == T1


def test_the_player_still_taps_the_rack_and_the_hands():
    """Only a ruled lane refuses the player: the rack (declared, not ruled) and the hands take a tap."""
    r = town()
    s = decide(decide(new_save(r), r, 0, TapCard(R)), r, 0, TapCard(H))
    assert (running(s, RACK), running(s, HANDS)) == (R, H)


def test_orders_drive_a_ruled_lane_exactly_as_an_unruled_one():
    """Invariant 58, second half: the same rules with ruled False give the same saves, for a town task changed by a
    store rule rising at a landing (x reaches Q at 100), an always rule, and a rack rule, over several landings."""
    r = town()
    verbs = (*mixing(), SetOrders((Order(AtLeast(StoreValue(X), Q, Q), TapCard(T2)), always(T1), always(R))))
    a, b = started(r, *verbs), started(unruled(r), *verbs)
    assert a == b and running(a, TOWN) == T1
    for t in (99, 100, 101, 250, 1000, 3700):
        a, b = advance(a, r, t), advance(b, unruled(r), t)
        assert a == b, t
    assert done(a, r, T1) == 1 and done(a, r, T2) >= 30


def test_an_outcomes_start_taps_a_ruled_lane_card():
    """Ruled lane: "an order, the queue or an Outcome taps it as on any lane": a trigger's start runs t1."""
    r = town(triggers=(TriggerDef(TriggerId("go"), AfterTime(10), Outcome(starts=(T1,))),))
    assert running(advance(new_save(r), r, 10), TOWN) == T1


def test_set_queue_refuses_an_entry_tapping_a_ruled_lane_card_wherever_it_stands():
    """The queue is the hands' plan: SetQueue with an entry tapping t1 raises InvalidVerbError (CONTRACT: set_queue
    with one is 422), first or behind another; a rack entry and a SetOrders tapping t1 are accepted (controls)."""
    r = town()
    s = new_save(r)
    for entries in ((QueueEntry(TapCard(T1), NEVER),),
                    (QueueEntry(TapCard(H), NEVER), QueueEntry(TapCard(TC), NEVER))):
        with pytest.raises(InvalidVerbError):
            decide(s, r, 0, SetQueue(entries))
    assert decide(s, r, 0, SetQueue((QueueEntry(TapCard(R), NEVER),))).queue == (QueueEntry(TapCard(R), NEVER),)
    assert running(decide(s, r, 0, SetOrders((always(T1),))), TOWN) == T1


def test_a_ruled_lane_card_is_never_mixable():
    """Ruled lane: a declared lane, so SaveMix holding its card raises InvalidVerbError."""
    r = town()
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, SaveMix(Mix(MixId("bad"), (CardShare(T1, 5000),))))


# ---- the lane's task ------------------------------------------------------------------------------------------

def test_a_rule_below_an_always_rule_acts_only_while_the_always_rules_card_cannot():
    """The lane's task: first rule that can act at each landing. Under always(t1), always(t2) the lane runs t1 at every
    landing and t2 never."""
    r = town()
    s = advance(started(r, SetOrders((always(T1), always(T2)))), r, 1000)
    assert done(s, r, T1) == 10 and done(s, r, T2) == 0 and running(s, TOWN) == T1


def test_the_default_task_follows_a_finished_one_off():
    """A one-off rule above the always rule: tc (cap 1) runs first; once completed its rule is passed over and the
    next always rule acts at that landing ("of several always rules ... the first that is not passed over"); the
    finished rule stays in the list, PASSED_OVER."""
    r = town(gated=False)
    s = started(r, SetOrders((always(TC), always(T1))))
    assert running(s, TOWN) == TC
    s = advance(s, r, 100)
    assert done(s, r, TC) == 1 and running(s, TOWN) == T1
    assert s.orders == (always(TC), always(T1)) and view(s, r).order_states == (PASSED, ON)


def test_a_task_change_takes_effect_at_the_lanes_next_landing():
    """SetOrders editing the rule: the card running runs to its completion (no cancel), the new task starts there."""
    r = town()
    s = decide(started(r, SetOrders((always(T1),))), r, 30, SetOrders((always(T2),)))
    assert running(s, TOWN) == T1
    assert running(advance(s, r, 99), TOWN) == T1
    s = advance(s, r, 100)
    assert done(s, r, T1) == 1 and running(s, TOWN) == T2


# ---- lane order and OUTRANKED (invariant 63) ---------------------------------------------------------------------

def test_lane_order_is_the_first_true_rule_tapping_the_running_card_and_later_ones_are_outranked():
    """Invariant 63: a waiting store rule, then always(t1), then always(t2): the lane runs t1, LaneBar.order is 1, and
    order_states are WAITING, ON, OUTRANKED."""
    r = town()
    s = started(r, SetOrders((Order(BIG, TapCard(T2)), always(T1), always(T2))))
    assert running(s, TOWN) == T1 and bar(s, r, TOWN).order == 1
    assert view(s, r).order_states == (WAITING, ON, OUTRANKED)


def test_lane_order_is_read_by_index_not_by_who_tapped():
    """Lane order: the first true order tapping the running card. always(t1) at index 1 taps t1 at 0; at 5 the rule
    at index 0 (also tapping t1) comes on, so the order becomes 0 and index 1 is OUTRANKED, mid-tap."""
    r = town()
    s = started(r, SetOrders((Order(AfterTime(5), TapCard(T1)), always(T1))))
    assert bar(s, r, TOWN).order == 1 and view(s, r).order_states == (WAITING, ON)
    s = advance(s, r, 5)
    assert running(s, TOWN) == T1 and bar(s, r, TOWN).order == 0
    assert view(s, r).order_states == (ON, OUTRANKED)


def test_an_earlier_true_rule_that_cannot_act_is_on_not_outranked():
    """OUTRANKED needs the lane's order below the rule's own index: always(tc) with tc locked is true and not dead, at
    index 0, while always(t1) at index 1 runs the lane, so it reads ON."""
    r = town()
    s = started(r, SetOrders((always(TC), always(T1))))
    assert running(s, TOWN) == T1 and bar(s, r, TOWN).order == 1
    assert view(s, r).order_states == (ON, ON)


def test_lane_order_is_none_while_free_or_when_no_true_rule_taps_what_it_runs():
    """Lane order is None while the lane is free (no rules), for the player's own tap (the rack) and for a rule that
    has since let go: AtMost(x, 0) taps t1 at 0 and falls at 1 as the mix makes x, while t1 still runs."""
    r = town()
    s = started(r, TapCard(R))
    assert bar(s, r, RACK).order is None and bar(s, r, HANDS).order is None
    s = started(r, *mixing(), SetOrders((Order(AtMost(StoreValue(X), 0, 0), TapCard(T1)),)))
    assert bar(s, r, TOWN).order == 0
    s = advance(s, r, 1)
    assert running(s, TOWN) == T1 and bar(s, r, TOWN).order is None and view(s, r).order_states == (WAITING,)


def test_only_rules_on_the_same_lane_are_outranked():
    """OUTRANKED reads its own card's lane: always(t1), always(r), always(h) each run their own lane, all ON, and each
    lane's LaneBar.order is its own rule's index."""
    r = town()
    s = started(r, SetOrders((always(T1), always(R), always(H))))
    assert view(s, r).order_states == (ON, ON, ON)
    assert [bar(s, r, x).order for x in (TOWN, RACK, HANDS)] == [0, 1, 2]
