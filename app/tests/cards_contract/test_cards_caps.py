"""Caps, `finished`, raises and greyed mixes (invariants 38-40; "Caps", "Greyed mix" in part "CARDS"): completions never
pass the effective cap; at the completion that reaches it `outcome` then `finished` land, the card's work stops, every
mix holding it greys whole, a tap of it ends and orders evaluate; a completed card cannot be tapped or saved into a mix;
a raise returns it and un-greys its mixes at that instant; a dead queue entry is passed over, kept and frozen while the
first live entry controls and pops on its own `until`."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, AtLeast, CapRaise, CardDef, CardId, CardShare, CompletedCard, Event, EventKind,
    Flow, InvalidVerbError, OrderVerb, LineKey, Mix, MixId, Order, Outcome, QueueEntry, Rules, RunKind, SaveMix, SetOrders,
    SetQueue, StandingBar, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, advance,
    advance_logged, decide, new_save, next_event, view,
)
from ashfall_app.engine.schedule import events
from cards_world import (
    Q, RACK, card_view, done, keys, lane, ledger, make, raised, rules, running_mix, save_mix, tap, val, with_mix, work,
)

Y, Z = StoreId("y"), StoreId("z")
C, M, M2, RZ = CardId("c"), CardId("m"), CardId("m2"), CardId("rz")
M0, M1, MM2 = MixId("m0"), MixId("m1"), MixId("mm2")
NEVER = AfterTime(10**9)
HOLDS = AtLeast(StoreValue(Y), 0, 0)
"""An `until` that holds and could fall (a store's value), so a dead entry holding it is kept, not settled."""


def world():
    """c: cap 2, a line per completion, an outcome line and a finished line; m and m2 make y and z; rz on the rack
    raises c's cap by one each completion."""
    return rules([StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
                 cards=[CardDef(C, 100, cap=2, lines=(LineKey("c.1"), LineKey("c.2")),
                                outcome=Outcome(lines=(LineKey("c.out"),)),
                                finished=Outcome(lines=(LineKey("c.fin"),))),
                        CardDef(M, 100, makes=(Flow(Y, 1000),)),
                        CardDef(M2, 100, makes=(Flow(Z, 1000),)),
                        CardDef(RZ, 300, lane=RACK, cap=10, outcome=Outcome(raises=(CapRaise(C, 1),)))],
                 lanes=[RACK])


def running(r: Rules):
    """m0 = {c 50%, m 50%} active from 0; m1 = {m2}; mm2 = {m} saved beside it."""
    s = save_mix(new_save(r), r, 0, {M2: BP}, "m1")
    s = save_mix(s, r, 0, {M: BP}, "mm2")
    return with_mix(s, r, 0, {C: 5000, M: 5000}, "m0")


def completed(r: Rules):
    """The save at 400, the instant c reaches its cap in m0."""
    return advance(running(r), r, 400)


def test_completions_stop_at_the_cap_and_finished_lands_once():
    """Invariant 38: two completions and no more; at the second, `outcome` then `finished`; the card's work stops and
    it moves to the Completed tab."""
    r = world()
    step = advance_logged(running(r), r, 5000)
    assert keys(step.lines) == [(200, "c.1"), (200, "c.out"), (400, "c.2"), (400, "c.out"), (400, "c.fin")]
    a = step.save
    assert done(a, r, C) == 2 and work(a, C).rate == 0
    v = view(a, r)
    assert C not in [cv.card for cv in v.cards]
    assert v.completed == (CompletedCard(C, 2),)


def test_the_mix_greys_whole_from_the_instant_its_card_completes():
    """Invariant 39: from the instant the active mix holds a completed card every one of its cards contributes 0 (each
    reads GREYED with its share kept), and the view lists the mix as greyed with no runs_out_at."""
    r = world()
    s = running(r)
    assert make(advance(s, r, 399), r, M, Y).per_hour == 500
    a = completed(r)
    e = make(a, r, M, Y)
    assert (e.run.kind, e.share_bp, e.per_hour) == (RunKind.GREYED, 5000, 0)
    assert work(a, M).rate == 0 and val(advance(a, r, 3000), r, Y) == val(a, r, Y) == 500 * 400
    v = view(a, r)
    assert v.greyed_mixes == (M0,) and v.runs_out_at is None
    mv = card_view(a, r, M)
    assert mv is not None and mv.run is RunKind.GREYED


def test_a_greyed_mix_has_no_runs_out_at_though_a_standing_action_drains_its_store():
    """View.runs_out_at: None for a greyed mix. burn, a standing action, keeps draining y, which the mix's card m also
    costs, so y still empties; but the mix runs nothing, so it does not run out of anything."""
    burn = ActionId("burn")
    r = rules([StoreDef(Y, 100 * Q, 50 * Q)], standing=[StandingDef(burn, costs=(Flow(Y, 2000),))],
              cards=[CardDef(M, 100, costs=(Flow(Y, 1000),)), CardDef(C, 50, cap=1)])
    s = with_mix(new_save(r), r, 0, {C: 5000, M: 5000})
    assert view(s, r).runs_out_at == ledger(s, r, Y).empties_at is not None
    a = advance(s, r, 100)
    assert view(a, r).greyed_mixes == (M0,) and ledger(a, r, Y).falling and ledger(a, r, Y).empties_at is not None
    assert view(a, r).runs_out_at is None


def test_a_greyed_mix_does_not_stop_a_standing_action():
    """Invariant 33 with 39: a standing action is outside the mix, so a greyed mix leaves it running at a full share
    (the view lists it FULL) while the mix's own cards contribute nothing."""
    gen = ActionId("gen")
    r = rules([StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)], standing=[StandingDef(gen, makes=(Flow(Z, 1000),))],
              cards=[CardDef(M, 100, makes=(Flow(Y, 1000),)), CardDef(C, 50, cap=1)])
    a = advance(with_mix(new_save(r), r, 0, {C: 5000, M: 5000}), r, 100)
    assert done(a, r, C) == 1 and view(a, r).greyed_mixes == (M0,)
    b = advance(a, r, 3100)
    assert val(b, r, Z) - val(a, r, Z) == 3000 * 1000 and val(b, r, Y) == val(a, r, Y)
    assert view(b, r).standing == (StandingBar(gen, RunKind.FULL),)


def test_a_completed_card_refuses_the_player_and_an_order_changes_nothing():
    """Invariant 38: a player's tap of a completed card and a SaveMix holding it raise InvalidVerbError; an order's tap
    of it changes nothing (the same lanes, cards and stores as with no order)."""
    r = world()
    a = completed(r)
    with pytest.raises(InvalidVerbError):
        tap(a, r, 400, C)
    with pytest.raises(InvalidVerbError):
        decide(a, r, 400, SaveMix(Mix(MixId("new"), (CardShare(C, 5000),))))
    by_order = decide(a, r, 400, SetOrders((Order(AfterTime(0), TapCard(C)),)))
    plain = decide(a, r, 400, SetOrders(()))
    assert (by_order.lanes, by_order.cards, by_order.stores) == (plain.lanes, plain.cards, plain.stores)


def test_an_outcome_that_starts_a_completed_card_changes_nothing():
    """Invariant 38: a tap by anything but the player (an order, the queue, an Outcome's starts) of a completed card
    changes nothing. rs, on the rack, starts c when it lands at 110; c completed at 100 and is not tapped, so the hands
    stay free and the mix is not yielded."""
    cap1, rs = CardId("cap1"), CardId("rs")
    r = rules([StoreDef(Y, 100 * Q, 0)], cards=[CardDef(cap1, 100, cap=1), CardDef(M, 100, makes=(Flow(Y, 1000),)),
                                                CardDef(rs, 10, lane=RACK, cap=1, outcome=Outcome(starts=(cap1,)))],
              lanes=[RACK])
    s = tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, cap1)
    a = advance(tap(advance(s, r, 100), r, 100, rs), r, 110)
    assert done(a, r, cap1) == 1 and lane(a, RACK).card is None
    assert lane(a, HANDS).card is None and make(a, r, M, Y).run.kind is RunKind.FULL


def test_a_tap_that_reaches_the_cap_ends_there():
    """"Caps": at the COMPLETION that reaches the cap mid-tap, `outcome` then `finished` land and the tap ends at that
    instant (its TAP_DONE follows), the lane free and the mix that holds the card greyed."""
    r = world()
    s = tap(advance(running(r), r, 300), r, 300, C)
    assert next_event(s, r) == Event(350, EventKind.COMPLETION, 0, C)
    step = advance_logged(s, r, 350)
    assert keys(step.lines) == [(350, "c.2"), (350, "c.out"), (350, "c.fin")]
    assert lane(step.save, HANDS).card is None
    assert make(step.save, r, M, Y).run.kind is RunKind.GREYED


def test_a_cap_raise_returns_the_card_and_ungreys_its_mix():
    """"Caps", CapRaise: rz's completion raises c's cap at 700; c leaves the Completed tab, m0 runs again with no player
    action, and c's next completion (past the base cap) emits the last line and lands `finished` again at the new
    cap."""
    r = world()
    s = tap(completed(r), r, 400, RZ)
    a = advance(s, r, 699)
    assert make(a, r, M, Y).run.kind is RunKind.GREYED
    step = advance_logged(s, r, 2000)
    b = advance(s, r, 700)
    assert raised(b, C) == 1
    assert make(b, r, M, Y).run.kind is RunKind.FULL and work(b, C).rate == 5000
    cv = card_view(b, r, C)
    assert cv is not None and (cv.completions, cv.cap) == (2, 3)
    assert view(b, r).completed == () and view(b, r).greyed_mixes == ()
    assert keys(step.lines) == [(900, "c.2"), (900, "c.out"), (900, "c.fin")]
    assert done(step.save, r, C) == 3


def test_a_raise_is_kept_for_a_card_that_has_not_run():
    """"Caps": the effective cap is cap + raised whatever the card's work is. rz raises c's cap before c has ever run
    (work 0, no rate): the raise is on the save and c's panel reads 0 of 3."""
    r = world()
    a = advance(tap(new_save(r), r, 0, RZ), r, 300)
    assert raised(a, C) == 1 and work(a, C).start_value == 0 and work(a, C).rate == 0
    cv = card_view(a, r, C)
    assert cv is not None and (cv.completions, cv.cap) == (0, 3)


def test_the_player_may_switch_to_a_greyed_mix_and_nothing_runs():
    """SwitchMix, "Greyed mix": the player's switch to a greyed mix is accepted; the mix stays greyed and nothing in it
    runs."""
    r = world()
    a = decide(completed(r), r, 400, SwitchMix(M1))
    b = decide(a, r, 400, SwitchMix(M0))
    assert b.active == M0
    assert make(b, r, M, Y).run.kind is RunKind.GREYED and make(b, r, M2, Z).per_hour == 0
    later = advance(b, r, 2000)
    assert val(later, r, Y) == val(b, r, Y) and val(later, r, Z) == val(b, r, Z)


def test_an_order_cannot_switch_to_a_greyed_mix_and_is_passed_over():
    """"Greyed mix", "Order mix": an order naming a greyed mix is passed over, so the next true order's mix runs; the
    player's own mix is unchanged."""
    r = world()
    before = completed(r)
    a = decide(before, r, 400, SetOrders((Order(AfterTime(0), SwitchMix(M0)),
                                           Order(AfterTime(0), SwitchMix(M1)))))
    assert running_mix(a, r) == M1 and a.active == before.active


@pytest.mark.parametrize("dead", [SwitchMix(M0), TapCard(C)], ids=["switch-to-greyed", "tap-of-completed"])
def test_the_queue_passes_over_a_dead_head_and_keeps_it(dead: OrderVerb):
    """QueueEntry, "Greyed mix": a head whose verb is dead (a switch to a greyed mix, a tap of a completed card) is
    passed over, so the next entry runs, and kept."""
    r = world()
    queue = (QueueEntry(dead, NEVER), QueueEntry(SwitchMix(M1), NEVER))
    a = decide(completed(r), r, 400, SetQueue(queue))
    assert running_mix(a, r) == M1 and a.queue == queue
    assert advance(a, r, 3000).queue == queue


@pytest.mark.parametrize("dead", [SwitchMix(M0), TapCard(C)], ids=["switch-to-greyed", "tap-of-completed"])
def test_a_queue_with_a_dead_head_behaves_as_the_queue_without_it(dead: OrderVerb):
    """Invariant 40, "Greyed mix": a queue whose head is dead behaves as the same queue with the head removed (the
    first live entry controlling and popping on its own `until`) and the head is still there after."""
    r = world()
    base = completed(r)
    rest = (QueueEntry(SwitchMix(M1), AtLeast(StoreValue(Z), Q, Q)), QueueEntry(SwitchMix(MM2), NEVER))
    head = QueueEntry(dead, NEVER)
    a = advance(decide(base, r, 400, SetQueue((head,) + rest)), r, 5400)
    b = advance(decide(base, r, 400, SetQueue(rest)), r, 5400)
    assert running_mix(b, r) == MM2 and b.queue == rest[1:]  # the control: the live entry popped once z reached an item
    assert a.queue == (head,) + b.queue
    assert replace(a, queue=()) == replace(b, queue=())


@pytest.mark.parametrize("dead", [SwitchMix(M0), TapCard(C)], ids=["switch-to-greyed", "tap-of-completed"])
def test_a_dead_entry_is_frozen_while_it_is_dead_even_if_its_until_holds(dead: OrderVerb):
    """"Greyed mix": a dead entry is never popped while dead unless its `until` cannot fall. Its `until` (HOLDS) holds
    from the start, yet the queue keeps it; the live entry behind it controls. A dead entry behind a live one that pops is just as frozen: the
    next live entry takes control past it."""
    r = world()
    base = completed(r)
    live = QueueEntry(SwitchMix(M1), AtLeast(StoreValue(Z), Q, Q))
    held = QueueEntry(dead, HOLDS)
    a = decide(base, r, 400, SetQueue((held, QueueEntry(SwitchMix(M1), NEVER))))
    assert running_mix(a, r) == M1 and advance(a, r, 3000).queue == a.queue
    assert len(a.queue) == 2
    b = advance(decide(base, r, 400, SetQueue((live, held, QueueEntry(SwitchMix(MM2), NEVER)))), r, 5400)
    assert running_mix(b, r) == MM2 and b.queue == (held, QueueEntry(SwitchMix(MM2), NEVER))


@pytest.mark.parametrize("dead", [SwitchMix(M0), TapCard(C)], ids=["switch-to-greyed", "tap-of-completed"])
def test_a_queue_of_only_dead_entries_acts_on_nothing_and_keeps_them(dead: OrderVerb):
    """"Greyed mix": with no live entry nothing controls, so no `until` is watched: a lone dead entry whose `until`
    already holds is neither acted on nor popped, now or later."""
    r = world()
    queue = (QueueEntry(dead, HOLDS),)
    a = decide(decide(completed(r), r, 400, SwitchMix(M1)), r, 400, SetQueue(queue))
    assert a.queue == queue and a.active == M1
    assert advance(a, r, 3000).queue == queue


def test_a_head_that_dies_at_the_instant_its_fallible_until_holds_is_not_popped_nor_is_the_next_entry():
    """EventKind.QUEUE_POP: a completion sorts before the pop. At 400 c completes, so the head, a switch to the mix
    holding c, is dead at the very instant its `until` (y reaching its value at 400, which could fall) first holds: it
    is kept, and the entry behind it, whose `until` does not hold, takes control and is not popped either."""
    r = world()
    y400 = val(completed(r), r, Y)
    assert val(advance(running(r), r, 399), r, Y) < y400
    queue = (QueueEntry(SwitchMix(M0), AtLeast(StoreValue(Y), y400, y400)), QueueEntry(SwitchMix(M1), NEVER))
    a = advance(decide(running(r), r, 0, SetQueue(queue)), r, 400)
    assert a.queue == queue and running_mix(a, r) == M1


def test_the_pop_event_watches_the_first_live_entry_not_a_dead_head():
    """EventKind.QUEUE_POP: the controlling entry's `until` is the one watched. The dead head's own `until` (z reaching
    its value at 500, which could fall) makes no event; the live entry's (900) does."""
    r = world()
    live = QueueEntry(SwitchMix(M1), AfterTime(900))
    z500 = val(advance(decide(completed(r), r, 400, SetQueue((live,))), r, 500), r, Z)
    a = decide(completed(r), r, 400, SetQueue((QueueEntry(SwitchMix(M0), AtLeast(StoreValue(Z), z500, z500)), live)))
    assert val(advance(a, r, 499), r, Z) < z500
    e = next_event(a, r)
    assert e is not None and (e.time, e.kind) == (900, EventKind.QUEUE_POP)
    assert not [x for x in events(a, r) if x.time == 500]


def test_a_raise_revives_a_dead_queue_head_at_that_instant():
    """Invariant 40, "Caps": the head was kept, so when a raise un-greys its mix the queue head controls again at that
    instant (orders and the queue evaluate after the raising completion)."""
    r = world()
    s = decide(completed(r), r, 400, SetQueue((QueueEntry(SwitchMix(M0), NEVER), QueueEntry(SwitchMix(M1), NEVER))))
    assert running_mix(s, r) == M1
    s = tap(s, r, 400, RZ)
    assert running_mix(advance(s, r, 699), r) == M1
    assert running_mix(advance(s, r, 700), r) == M0


def test_a_revived_entry_whose_until_already_holds_pops_at_once():
    """"Greyed mix": when a raise revives a dead entry it controls again at that instant and, its `until` (HOLDS)
    already holding, pops at once: the queue is the live entry alone and the live entry runs."""
    r = world()
    tail = QueueEntry(SwitchMix(M1), NEVER)
    s = decide(completed(r), r, 400, SetQueue((QueueEntry(SwitchMix(M0), HOLDS), tail)))
    assert running_mix(s, r) == M1 and len(s.queue) == 2
    s = tap(s, r, 400, RZ)
    b = advance(s, r, 699)
    assert running_mix(b, r) == M1 and len(b.queue) == 2
    c = advance(s, r, 700)
    assert c.queue == (tail,) and running_mix(c, r) == M1
