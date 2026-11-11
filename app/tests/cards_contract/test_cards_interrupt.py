"""A card stopped mid-completion (invariant 41, "Inputs against a dry store", "Requires"): in the mix a dry input pauses
it and a false requires makes it WAITING, and either way its work stops; a tap whose card is paused by a dry store or
whose requires turn false or whose speed falls to 0 ends at once, interrupted (work.interrupt): the card keeps its work
and its Pause, the lane frees, nothing lands, the mix resumes and orders evaluate. A tap whose work has reached its
boundary as the store runs dry has landed. A Pause belongs to the card, not to who ran it."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, AfterTime, Amount, AtLeast, Blocker, CardDef, CardId, ChipDef, ChipId, Event, EventKind, Flow,
    InvalidVerbError, LaneId, LaneSpeed, LaneState, LineKey, Order, Pause, RunKind, SetOrders, StandingDef, StoreDef, StoreId,
    StoreValue, TapCard, WorkRef, ActionId, advance, advance_logged, decide, new_save, next_event, Modifier,
)
from ashfall_app.engine import work as engine_work
from cards_world import (
    Q, add, card_view, cost, keys, lane, ledger, make, mul, refill, rules, tap, val, view_of, with_mix, work,
)

X, Z, W, V, U, Y = (StoreId(n) for n in ("x", "z", "w", "v", "u", "y"))
C, M, D, CR, CW, CD = (CardId(n) for n in ("c", "m", "d", "cr", "cw", "cd"))
GEN, FIRE, DRAIN, GROW = (ActionId(n) for n in ("gen", "fire", "drain", "grow"))
RACK = LaneId("rack")


def dry_world():
    """x holds exactly c's input; gen makes 18_000/s, fire burns 36_000/s and a tap of c draws 18_000/s, so x runs dry
    at t=100, half way through a 200 s tap."""
    return rules([StoreDef(X, 100 * Q, Q), StoreDef(Z, 100 * Q, 0)],
                 standing=[StandingDef(GEN, makes=(Flow(X, 18_000),)), StandingDef(FIRE, costs=(Flow(X, 36_000),))],
                 cards=[CardDef(C, 200, inputs=(Amount(X, Q),), lines=(LineKey("c.tap"),)),
                        CardDef(M, 100, makes=(Flow(Z, 1000),)),
                        CardDef(D, 50)])


def test_a_tap_whose_store_runs_dry_ends_there_interrupted():
    """"Inputs against a dry store": x empties at 100 (a STORE_LIMIT); the dry rule pauses the tapped card first (HANDS
    after standing actions, last first), which interrupts the tap: no line, the lane free, c keeping its half bar and
    no longer running, and the mix running again; the tap, queued at the front, takes up its kept work once x holds
    the rest of its input and lands."""
    r = dry_world()
    s = tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, C)
    assert next_event(s, r) == Event(100, EventKind.STORE_LIMIT, 0, X)
    step = advance_logged(s, r, 100)
    a = step.save
    assert keys(step.lines) == []
    assert lane(a, HANDS).card is None
    assert work(a, C).start_value == 100 * BP and work(a, C).rate == 0
    assert make(a, r, M, Z).run.kind is RunKind.FULL
    b = advance(a, r, 5000)
    assert lane(b, HANDS).card is None and not b.queue and work(b, C).start_value == 200 * BP


def test_a_hands_tap_a_dry_store_interrupts_goes_to_the_queue_front():
    """"Inputs against a dry store": the interrupted hands tap is the player's, so it goes to the queue's front as
    cut_in does, with its work kept, and starts again once the store holds the rest of its input."""
    r = dry_world()
    a = advance(tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, C), r, 100)
    assert lane(a, HANDS).card is None and work(a, C).start_value == 100 * BP
    assert a.queue and a.queue[0].verb == TapCard(C)


def test_an_interrupted_tap_makes_orders_evaluate():
    """work.interrupt: orders and the queue evaluate after it, as after a landing. A true order to tap d could not act
    while c held the hands; the interrupt frees them and d starts at that instant."""
    r = dry_world()
    s = tap(new_save(r), r, 0, C)
    s = decide(s, r, 0, SetOrders((Order(AfterTime(0), TapCard(D)),)))
    assert lane(s, HANDS).card == C
    assert lane(advance(s, r, 99), HANDS).card == C
    assert lane(advance(s, r, 100), HANDS).card == D


def req_world():
    """cr requires w >= 1 item; w starts one unit short of 2 items and drains 36_000/s, so the requires turn false at
    exactly t=100, half way through a 200 s tap."""
    return rules([StoreDef(W, 100 * Q, 2 * Q - 1)],
                 standing=[StandingDef(DRAIN, costs=(Flow(W, 36_000),))],
                 cards=[CardDef(CR, 200, requires=(AtLeast(StoreValue(W), Q, Q),), lines=(LineKey("cr.tap"),))])


def test_a_tap_whose_requires_turn_false_ends_there_interrupted():
    """"Requires": they hold at a tap's start and while the card runs; a REQUIRES event falls at the second the truth
    changes, and the tap ends there, interrupted, keeping its work and emitting nothing."""
    r = req_world()
    s = tap(new_save(r), r, 0, CR)
    assert lane(s, HANDS).card == CR
    assert next_event(s, r) == Event(100, EventKind.REQUIRES, 0, CR)
    step = advance_logged(s, r, 100)
    assert keys(step.lines) == []
    assert lane(step.save, HANDS).card is None
    assert work(step.save, CR).start_value == 100 * BP and work(step.save, CR).rate == 0
    assert lane(advance(s, r, 99), HANDS).card == CR


def test_a_tap_interrupted_by_a_requires_makes_orders_evaluate():
    """work.interrupt after a requires: as after a dry store, orders and the queue evaluate at once. A true order to tap d
    could not act while cr held the hands; the requires turning false at 100 frees them and d starts at that instant."""
    r = rules([StoreDef(W, 100 * Q, 2 * Q - 1)], standing=[StandingDef(DRAIN, costs=(Flow(W, 36_000),))],
              cards=[CardDef(CR, 200, requires=(AtLeast(StoreValue(W), Q, Q),)), CardDef(D, 50)])
    s = decide(tap(new_save(r), r, 0, CR), r, 0, SetOrders((Order(AfterTime(0), TapCard(D)),)))
    assert lane(s, HANDS).card == CR and lane(advance(s, r, 99), HANDS).card == CR
    assert lane(advance(s, r, 100), HANDS).card == D


def test_a_waiting_card_names_its_first_unmet_requires_and_it_runs_the_second_it_holds():
    """"Requires in the mix": WAITING names the first unmet requires by index, and a requires one second away is an event
    like any other. cw requires v >= 1 item and v >= 2 items; v grows an item per 100 s."""
    two = (AtLeast(StoreValue(V), Q, Q), AtLeast(StoreValue(V), 2 * Q, 2 * Q))
    r = rules([StoreDef(V, 100 * Q, 0), StoreDef(Y, 100 * Q, 0)], standing=[StandingDef(GROW, makes=(Flow(V, 36_000),))],
              cards=[CardDef(CW, 100, requires=two, makes=(Flow(Y, 1000),))])
    s = with_mix(new_save(r), r, 0, {CW: BP})
    assert make(s, r, CW, Y).run.condition_index == 0
    assert make(advance(s, r, 100), r, CW, Y).run.condition_index == 1
    near = rules([StoreDef(V, 100 * Q, Q - 36_000), StoreDef(Y, 100 * Q, 0)],
                 standing=[StandingDef(GROW, makes=(Flow(V, 36_000),))],
                 cards=[CardDef(CW, 100, requires=(AtLeast(StoreValue(V), Q, Q),), makes=(Flow(Y, 1000),))])
    assert next_event(with_mix(new_save(near), near, 0, {CW: BP}), near) == Event(1, EventKind.REQUIRES, 0, CW)


def test_a_mix_card_waits_on_its_requires_and_its_bar_waits_with_it():
    """"Requires": in the mix a false requires makes the card WAITING (0/1, its share kept, condition_index naming the
    first unmet one); nothing it makes runs and its work holds still; it runs the instant they hold (REQUIRES)."""
    r = rules([StoreDef(V, 100 * Q, 0), StoreDef(Y, 100 * Q, 0)],
              standing=[StandingDef(GROW, makes=(Flow(V, 36_000),))],
              cards=[CardDef(CW, 100, requires=(AtLeast(StoreValue(V), Q, Q),), makes=(Flow(Y, 1000),))])
    s = with_mix(new_save(r), r, 0, {CW: BP})
    e = make(s, r, CW, Y)
    assert (e.run.kind, e.run.condition_index, e.share_bp, e.per_hour) == (RunKind.WAITING, 0, BP, 0)
    assert work(s, CW).rate == 0
    assert next_event(s, r) == Event(100, EventKind.REQUIRES, 0, CW)
    a = advance(s, r, 100)
    assert make(a, r, CW, Y).run.kind is RunKind.FULL and work(a, CW).rate == BP
    assert val(a, r, Y) == 0


def test_a_mix_card_paused_on_a_dry_input_stops_its_bar_and_starves_the_line():
    """Invariant 41, "Inputs against a dry store": the input u runs dry at 50 and pauses cd by the running-dry rule; its
    work stops with it, so a completion is never finished unpaid; the view shows it PAUSED and u's ledger line
    starved."""
    r = rules([StoreDef(U, 100 * Q, Q // 2)], cards=[CardDef(CD, 100, inputs=(Amount(U, Q),)), refill(U)])
    s = with_mix(new_save(r), r, 0, {CD: BP})
    a = advance(s, r, 50)
    assert val(a, r, U) == 0 and a.pauses == (Pause(CD, U, 3600 * 36_000),)
    e = cost(a, r, CD, U)
    assert (e.run.kind, e.run.store, e.per_hour) == (RunKind.PAUSED, U, 0)
    assert work(a, CD).start_value == 50 * BP and work(a, CD).rate == 0
    assert work(advance(a, r, 3000), CD).start_value == 50 * BP
    cv = card_view(a, r, CD)
    assert cv is not None and cv.run is RunKind.PAUSED
    assert ledger(a, r, U).starved


@pytest.mark.parametrize("capped", [False, True], ids=["uncapped", "capped"])
def test_a_tap_whose_store_empties_as_it_lands_has_landed(capped: bool):
    """"Inputs against a dry store": a ready tap may start with exactly the rest of its input in store, which then
    reaches 0 at the very second the work reaches the boundary (STORE_LIMIT sorts before COMPLETION and TAP_DONE). The
    card has finished: the completion and the landing stand, with their line, and the dry rule passes it over: no
    interrupt, no Pause."""
    line = (LineKey("c.1"), LineKey("c.2")) if capped else (LineKey("c.tap"),)
    r = rules([StoreDef(X, 100 * Q, Q)],
              cards=[CardDef(C, 100, inputs=(Amount(X, Q),), cap=2 if capped else None, lines=line)])
    s = tap(new_save(r), r, 0, C)
    assert engine_work.ready(new_save(r), r, C) and lane(s, HANDS).card == C
    assert lane(advance(s, r, 99), HANDS).card == C
    step = advance_logged(s, r, 100)
    a = step.save
    assert keys(step.lines) == [(100, line[0])]
    assert lane(a, HANDS) == LaneState(HANDS) and a.pauses == ()
    assert work(a, C).start_value == 100 * BP and engine_work.completions(a, r, C) == 1
    assert val(a, r, X) == 0


@pytest.mark.parametrize("capped", [False, True], ids=["uncapped", "capped"])
def test_a_mix_card_whose_store_runs_dry_at_its_boundary_is_paused_with_one_completion(capped: bool):
    """DESIGN.txt, "Inputs against a dry store" (the last decision): work that reaches a completion boundary at the
    second its store runs dry has finished that completion, and counts; a mix card carries on into the next, which
    nothing has paid for, so the dry rule pauses it, capped or not. The rejected reading passed it over and ran it on
    with x at 0 (10 completions by t = 1_000). The same world tapped lands instead: the card stops there."""
    line = (LineKey("c.1"), LineKey("c.2"), LineKey("c.3")) if capped else (LineKey("c.tap"),)
    r = rules([StoreDef(X, 100 * Q, Q)],
              cards=[CardDef(C, 100, inputs=(Amount(X, Q),), cap=5 if capped else None, lines=line), refill(X)])
    s = with_mix(new_save(r), r, 0, {C: BP})
    assert next_event(s, r) == Event(100, EventKind.STORE_LIMIT, 0, X)
    for t in (100, 1_000):
        a = advance(s, r, t)
        assert engine_work.completions(a, r, C) == 1, t
        assert val(a, r, X) == 0, t
        assert cost(a, r, C, X).run.kind is RunKind.PAUSED, t
        assert [p.runner for p in a.pauses] == [C], t
        assert work(a, C).rate == 0, t


def test_the_same_world_tapped_lands_at_the_boundary_and_stops():
    """The companion of the mix case above: a tap stops at its boundary, so the dry rule passes it over."""
    r = rules([StoreDef(X, 100 * Q, Q)], cards=[CardDef(C, 100, inputs=(Amount(X, Q),), lines=(LineKey("c.tap"),))])
    s = tap(new_save(r), r, 0, C)
    step = advance_logged(s, r, 100)
    assert keys(step.lines) == [(100, "c.tap")]
    for t in (100, 1_000):
        a = advance(s, r, t)
        assert engine_work.completions(a, r, C) == 1 and lane(a, HANDS) == LaneState(HANDS) and a.pauses == ()


def pause_world():
    """y holds half an item and gen refills it at 18_000/s; a tap of c (200 s, costing y at 36_000/s) empties it at 100,
    half way. m, in the mix, makes z. c is in the mix too."""
    return rules([StoreDef(Y, 100 * Q, Q // 2), StoreDef(Z, 100 * Q, 0)],
                 standing=[StandingDef(GEN, makes=(Flow(Y, 18_000),))],
                 cards=[CardDef(C, 200, costs=(Flow(Y, 36_000),)), CardDef(M, 100, makes=(Flow(Z, 1000),))])


HOUR_OF_C = 3600 * 36_000
"""One hour of c's cost at a full share, in quantity units: where its Pause resumes (the store refills at 18_000/s)."""


def test_a_pause_belongs_to_the_card_and_outlives_the_tap_that_met_it():
    """"Inputs against a dry store": y empties at 100 and the dry rule pauses the tapped c, interrupting the tap. The
    Pause stays on the card: in the mix (where c also is) it reads PAUSED, its bar holds still, and it resumes only when
    y refills to an hour of the cost it was paused at (a tap's, at a full share), a RESUME at the exact second; the
    queued tap then starts again from its kept work and the card runs at the tap's full speed."""
    r = pause_world()
    s = tap(with_mix(new_save(r), r, 0, {C: 5000, M: 5000}), r, 0, C)
    a = advance(s, r, 100)
    assert lane(a, HANDS) == LaneState(HANDS)
    assert a.pauses == (Pause(C, Y, HOUR_OF_C),)
    assert work(a, C).start_value == 100 * BP and work(a, C).rate == 0
    cv = card_view(a, r, C)
    assert cv is not None and cv.run is RunKind.PAUSED and cv.by is None
    assert make(a, r, M, Z).run.kind is RunKind.FULL
    b = advance(a, r, 3000)
    assert b.pauses == a.pauses and work(b, C).start_value == 100 * BP
    e = next_event(b, r)
    assert e is not None and (e.time, e.kind, e.subject) == (7300, EventKind.RESUME, "c")
    assert advance(b, r, 7299).pauses == a.pauses
    c = advance(b, r, 7300)
    assert c.pauses == () and lane(c, HANDS).card == C and work(c, C).rate == BP


def test_a_tap_of_a_paused_card_waits_for_the_resume():
    """Blocker, "Inputs against a dry store": a tap needs no Pause on the card. Its Blocker is AtLeast(the pause's store,
    resume_at) and ready_at the second the store gets there; the player's tap before then is a failed tap (the save
    unchanged), an order's tap does nothing, and the order's tap starts at the resume (READY)."""
    r = pause_world()
    a = advance(tap(with_mix(new_save(r), r, 0, {C: 5000, M: 5000}), r, 0, C), r, 1000)
    want = Blocker(AtLeast(StoreValue(Y), HOUR_OF_C, HOUR_OF_C), 7300)
    assert engine_work.blocker(a, r, C) == want and not engine_work.ready(a, r, C)
    assert view_of(a, r, C).blocker == want
    assert tap(a, r, 1000, C) == a
    o = decide(a, r, 1000, SetOrders((Order(AfterTime(0), TapCard(C)),)))
    assert lane(o, HANDS) == LaneState(HANDS) and lane(advance(o, r, 7299), HANDS) == LaneState(HANDS)
    b = advance(o, r, 7300)
    assert lane(b, HANDS).card == C and b.pauses == ()


def dry_again_world():
    """As pause_world, but m, the mix card, costs y too: when the interrupt frees the mix, y is still dry."""
    return rules([StoreDef(Y, 100 * Q, Q // 2)], standing=[StandingDef(GEN, makes=(Flow(Y, 18_000),))],
                 cards=[CardDef(C, 200, costs=(Flow(Y, 36_000),)), CardDef(M, 100, costs=(Flow(Y, 36_000),))])


def test_after_an_interrupt_the_dry_rule_runs_again_over_what_then_runs():
    """"Inputs against a dry store": the interrupt frees the mix at the same instant and the dry rule runs again over
    what then runs, keeping the pauses it has and adding new ones last first: c's tap is paused and interrupted, the mix
    resumes drawing the still dry y, so m is paused too, in runner order; nothing is recomputed from scratch."""
    r = dry_again_world()
    s = tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, C)
    a = advance(s, r, 100)
    assert lane(a, HANDS) == LaneState(HANDS)
    assert a.pauses == (Pause(C, Y, HOUR_OF_C), Pause(M, Y, HOUR_OF_C))
    assert cost(a, r, M, Y).run.kind is RunKind.PAUSED and work(a, M).rate == 0
    assert val(a, r, Y) == 0 and val(advance(a, r, 200), r, Y) == 18_000 * 100


def test_a_pause_resumes_at_the_second_the_store_gets_there():
    """Pause.resume_at, RESUME: the event falls at the first second the store holds resume_at, not the one before. c, at
    a full share, costs 11 units a second, so it resumes at 39_600; y holds 8, gen refills 7 a second against the 11 and
    y is empty at 2; 39_600 / 7 is 5657.14, so y gets there 5658 s later, at 5660 (and 39_599 would be there at 5659)."""
    r = rules([StoreDef(Y, 100 * Q, 8)], standing=[StandingDef(GEN, makes=(Flow(Y, 7),))],
              cards=[CardDef(C, 100, costs=(Flow(Y, 11),))])
    a = advance(with_mix(new_save(r), r, 0, {C: BP}), r, 2)
    assert a.pauses == (Pause(C, Y, 39_600),) and val(a, r, Y) == 0
    assert next_event(a, r) == Event(5660, EventKind.RESUME, 1, "c")


@pytest.mark.parametrize("by, hour", [("tap", 36_000), ("mix", 18_000)])
def test_a_pause_resumes_at_an_hour_of_the_cost_it_was_paused_at(by: str, hour: int):
    """Pause.resume_at: an hour of the cost line the card was paused at, at its running share: a tap's at a full share
    (BP), a mix card's at its mix share (50%), lump inputs included (c's input Q over 100 s is 36_000/s at BP)."""
    r = rules([StoreDef(U, 100 * Q, Q)], standing=[StandingDef(FIRE, costs=(Flow(U, 36_000),))],
              cards=[CardDef(CD, 100, inputs=(Amount(U, Q),))])
    s = new_save(r)
    s = tap(s, r, 0, CD) if by == "tap" else with_mix(s, r, 0, {CD: 5000})
    a = advance(s, r, 100)
    assert [p for p in a.pauses if p.runner == CD] == [Pause(CD, U, 3600 * hour)]


@pytest.mark.parametrize("stop", [add(WorkRef(CD), -BP, "halt"), mul(LaneSpeed(RACK), 0, "halt")],
                         ids=["work-speed", "lane-speed"])
def test_a_tap_whose_speed_falls_to_zero_is_interrupted(stop: Modifier):
    """"Inputs against a dry store" (a tap ends, interrupted, when its card's speed falls to 0): a chip stops a rack
    tap's work at 50 of 200 s (a hands tap keeps its start speed: test_a_hands_tap_keeps_its_start_speed). The tap
    ends there, the card keeps its half bar and nothing lands; the mix runs on, and a tap now is refused (tap_seconds
    None)."""
    r = rules([StoreDef(Z, 100 * Q, 0)],
              cards=[CardDef(CD, 200, lane=RACK, lines=(LineKey("cd.tap"),)), CardDef(M, 100, makes=(Flow(Z, 1000),))],
              lanes=[RACK], chips=[ChipDef(ChipId("halt"), AfterTime(50), (stop,), None, None)])
    s = tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, CD)
    assert lane(advance(s, r, 49), RACK).card == CD
    step = advance_logged(s, r, 50)
    a = step.save
    assert keys(step.lines) == [] and lane(a, RACK) == LaneState(RACK)
    assert work(a, CD).start_value == 50 * BP and work(a, CD).rate == 0
    assert make(a, r, M, Z).run.kind is RunKind.FULL
    assert work(advance(a, r, 5000), CD).start_value == 50 * BP
    assert engine_work.tap_seconds(a, r, CD) is None
    with pytest.raises(InvalidVerbError):
        tap(a, r, 50, CD)
