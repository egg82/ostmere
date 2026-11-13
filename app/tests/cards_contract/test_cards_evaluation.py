"""Evaluation applies every verb (DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Evaluation applies every
verb", "Evaluation after a cascade", "A chip that shows or hides evaluates", "Shipping the evaluation change", invariant
57). One evaluation is a loop: the TapCard of the first true order whose card can act (speed above 0 included), else,
while no order's mix runs, the controlling queue entry's verb; applied, then picked again until nothing can act or the
verb changed nothing. Two lanes ready at one instant both start; a speed-0 tap is skipped and acts the instant a chip
brings its speed back; after a cascade a READY at T + 1 also covers a queue verb with no card."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, Amount, AtLeast, CardCount, CardDef, CardId, ChipDef, ChipId, Event, EventKind, Flow,
    InvalidVerbError, LaneSpeed, MixId, Modifier, Order, Outcome, QueueEntry, Rules, Save, SaveMix, SetOrders,
    SetQueue, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, Verb, WorkRef,
    advance, decide, decode, encode, new_save, next_event, validate_rules, view,
)
from cards_gen import Scenario, condition_st, few, order_verb_st, scenario_st, span, timeline, try_decide
from cards_world import Q, RACK, add, done, lane, mul, rules, running_mix, save_mix, tap, view_of

X, W = StoreId("x"), StoreId("w")
H, H2, R, CP, M0C, M1C = (CardId(n) for n in ("h", "h2", "r", "cp", "m0c", "m1c"))
M0, M1 = MixId("m0"), MixId("m1")
ALWAYS = AfterTime(0)
NEVER = AfterTime(10**9)


def world(max_firings: int = 1000, *, standing: list[StandingDef] | None = None, chips: list[ChipDef] | None = None,
          triggers: list[TriggerDef] | None = None, w: int = 0, capped: int | None = None) -> Rules:
    """h, h2 on the hands and r on the rack, 100 s a completion (`capped`: h and r get that cap); cp capped at 3;
    m0c and m1c for the two mixes. w is a store for chips to read."""
    return rules([StoreDef(X, 100 * Q, 0), StoreDef(W, 100 * Q, w)],
                 cards=[CardDef(H, 100, cap=capped), CardDef(H2, 100), CardDef(R, 100, lane=RACK, cap=capped),
                        CardDef(CP, 100, cap=3), CardDef(M0C, 100, makes=(Flow(X, 10),)),
                        CardDef(M1C, 100, makes=(Flow(X, 20),))],
                 lanes=[RACK], standing=standing, chips=chips, triggers=triggers, max_firings=max_firings)


def both_mixes(s: Save, r: Rules) -> Save:
    """m0 = {m0c} and m1 = {m1c} saved, the player on m0."""
    s = save_mix(save_mix(s, r, 0, {M0C: BP}, "m0"), r, 0, {M1C: BP}, "m1")
    return decide(s, r, 0, SwitchMix(M0))


def busy_at_0(r: Rules, *cards: CardId, mods: tuple[Modifier, ...] = ()) -> Save:
    """The player taps each card at 0 (a player's tap does not evaluate), so its lane lands at 100."""
    s = new_save(r, mods)
    for c in cards:
        s = tap(s, r, 0, c)
    return s


# ---- the loop: every verb that can act -------------------------------------------------------------------------

def test_two_lanes_with_ready_tap_orders_both_start_at_the_set_orders_instant():
    """Invariant 57, "in particular": a hands order and a rack order, both true with a ready card, both run once
    SetOrders evaluates, in either order sequence."""
    r = world()
    for orders in ((Order(ALWAYS, TapCard(H)), Order(ALWAYS, TapCard(R))),
                   (Order(ALWAYS, TapCard(R)), Order(ALWAYS, TapCard(H)))):
        s = decide(new_save(r), r, 0, SetOrders(orders))
        assert (lane(s, HANDS).card, lane(s, RACK).card) == (H, R), orders


def test_two_lanes_landing_at_one_instant_both_retap():
    """Invariant 57: "two lanes landing at one instant, each with a true order whose card is ready, are both running
    at that instant". The player's taps put h and r on their lanes at 0 (SetOrders then finds both busy); both land
    at 100 and both orders re-tap there."""
    r = world()
    s = decide(busy_at_0(r, H, R), r, 0, SetOrders((Order(ALWAYS, TapCard(H)), Order(ALWAYS, TapCard(R)))))
    a = advance(s, r, 100)
    assert done(a, r, H) == 1 and done(a, r, R) == 1
    assert (lane(a, HANDS).card, lane(a, RACK).card) == (H, R)


def test_a_rack_tap_order_and_the_queue_head_both_act_at_one_landing():
    """"Shipping the evaluation change": the day-one defect, a rack tap order and a hands verb from the queue's head
    able to act at one instant. Both lanes land at 100; the order re-taps r and the queue's head taps h2."""
    r = world()
    s = decide(busy_at_0(r, H, R), r, 0, SetOrders((Order(ALWAYS, TapCard(R)),)))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(H2), NEVER),)))
    a = advance(s, r, 100)
    assert (lane(a, HANDS).card, lane(a, RACK).card) == (H2, R)


def test_the_queue_heads_switch_is_applied_after_a_tap_order_in_the_same_evaluation():
    """"Evaluation applies every verb", "Queue mix": r lands at 100, its count pops the queue's first entry, and the head
    is now "switch to m1": the order re-taps r and m1 runs from that instant, with nothing applied for the switch."""
    r = world()
    s = decide(both_mixes(busy_at_0(r, R), r), r, 0, SetOrders((Order(ALWAYS, TapCard(R)),)))
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(M0), AtLeast(CardCount(R), 1, 1)),
                                  QueueEntry(SwitchMix(M1), NEVER))))
    assert running_mix(s, r) == M0
    a = advance(s, r, 100)
    assert lane(a, RACK).card == R and running_mix(a, r) == M1 and len(a.queue) == 1


def test_tap_orders_come_before_the_queue_on_one_lane():
    """The controlling verb, in order: a true tap order's TapCard, then the queue's. h lands at 100; its order re-taps
    it, so the queue's tap of h2 (another hands card) waits and stays queued."""
    r = world()
    s = decide(busy_at_0(r, H), r, 0, SetOrders((Order(ALWAYS, TapCard(H)),)))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(H2), NEVER),)))
    a = advance(s, r, 100)
    assert lane(a, HANDS).card == H and len(a.queue) == 1


def test_the_queue_is_not_read_while_an_orders_mix_runs():
    """"else, while no order's mix runs, the verb of the controlling queue entry": a latched mix order runs m1, so at
    r's landing the rack order re-taps r and the queue's tap of h is not applied, though the hands are free."""
    r = world()
    s = both_mixes(busy_at_0(r, R), r)
    s = decide(s, r, 0, SetOrders((Order(ALWAYS, SwitchMix(M1)), Order(ALWAYS, TapCard(R)))))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(H), NEVER),)))
    a = advance(s, r, 100)
    assert view(a, r).mix_order == 0
    assert lane(a, RACK).card == R and lane(a, HANDS).card is None


# ---- speed 0: skipped when choosing, acting once a chip brings the speed back --------------------------------------

def test_a_tap_order_at_speed_0_is_skipped_and_a_later_order_acts():
    """"Ready" includes speed above 0 (tap_seconds not None): h's work runs at 0 (a WorkRef at 0%), so its order is
    skipped when choosing and the next order's h2 takes the hands at once."""
    r = world()
    s = new_save(r, (mul(WorkRef(H), 0, "save"),))
    assert view_of(s, r, H).tap_s is None and view_of(s, r, H).blocker is None
    s = decide(s, r, 0, SetOrders((Order(ALWAYS, TapCard(H)), Order(ALWAYS, TapCard(H2)))))
    assert lane(s, HANDS).card == H2


def test_a_queue_head_at_speed_0_waits_and_holds_the_entries_behind_it():
    """"only the queue's head (which waits, never passed over) can be a chosen verb that changes nothing": a head
    tapping h at speed 0 is not skipped, so h2 behind it does not tap."""
    r = world()
    s = new_save(r, (mul(WorkRef(H), 0, "save"),))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(H), NEVER), QueueEntry(TapCard(H2), NEVER))))
    assert lane(s, HANDS).card is None and len(s.queue) == 2


BURN, GEN = ActionId("burn"), ActionId("gen")
TIRED, RESTED = ChipId("tired"), ChipId("rested")


def _speed_world(shows: bool) -> tuple[Rules, tuple[Modifier, ...]]:
    """The hands at speed 0 until a chip turns at about 100 to 200 s, with nothing else falling then. hides: w starts at
    3 items and burns an item per 100 s; "tired" (w >= 2 items) holds the hands at 0% and clears as w drops. shows: the
    save holds the hands at -100%; w fills an item per 100 s and "rested" (w >= 2 items) adds +100% when it shows."""
    if shows:
        chip = ChipDef(RESTED, AtLeast(StoreValue(W), 2 * Q, 2 * Q), (add(LaneSpeed(HANDS), BP, "rested"),))
        return (world(standing=[StandingDef(GEN, makes=(Flow(W, 36_000),))], chips=[chip]),
                (add(LaneSpeed(HANDS), -BP, "save"),))
    chip = ChipDef(TIRED, AtLeast(StoreValue(W), 2 * Q, 2 * Q), (mul(LaneSpeed(HANDS), 0, "tired"),))
    return world(standing=[StandingDef(BURN, costs=(Flow(W, 36_000),))], chips=[chip], w=3 * Q), ()


def test_a_skipped_tap_acts_at_the_instant_a_chip_turning_brings_its_speed_back():
    """"A chip that shows or hides evaluates" and invariant 57 "across a chip turning": the order's h is skipped at
    speed 0, nothing else evaluates, and at the CHIP instant that returns the hands' speed above 0 the order taps h.
    Both ways: a chip that held the speed at 0 hiding, and a chip that restores it showing."""
    for shows in (False, True):
        r, mods = _speed_world(shows)
        s = decide(new_save(r, mods), r, 0, SetOrders((Order(ALWAYS, TapCard(H)),)))
        assert view_of(s, r, H).tap_s is None and lane(s, HANDS).card is None, shows
        e = next_event(s, r)
        assert e is not None and e.kind is EventKind.CHIP, (shows, e)
        before = advance(s, r, e.time - 1)
        assert lane(before, HANDS).card is None and view_of(before, r, H).tap_s is None, shows
        at = advance(s, r, e.time)
        assert view(at, r).chips == ((RESTED,) if shows else ()), shows
        assert lane(at, HANDS).card == H, shows


# ---- after a cascade ---------------------------------------------------------------------------------------------

def _cascading_switch(max_firings: int, then: MixId) -> tuple[Rules, Save]:
    """The player taps cp (cap 3) at 0; the queue switches to m0 (already active) until cp has a completion, then to
    `then`. At 100 cp's COMPLETION and TAP_DONE are two firings and the pop makes the switch to `then` the head."""
    r = world(max_firings)
    s = tap(both_mixes(new_save(r), r), r, 0, CP)
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(M0), AtLeast(CardCount(CP), 1, 1)),
                                  QueueEntry(SwitchMix(then), NEVER))))
    assert s.active == M0 and lane(s, HANDS).card == CP
    return r, s


def test_a_queue_mix_runs_at_a_pop_past_the_firing_cap():
    """"Queue mix", "Firing cap": with a cap of 2, evaluation is suspended at 100, yet the pop that makes the switch to
    m1 the head still runs m1 at that instant (no verb waits, so no READY falls at 101). The control, with room for the
    firings, runs m1 at 100 too."""
    r, s = _cascading_switch(1000, M1)
    assert running_mix(advance(s, r, 100), r) == M1
    r, s = _cascading_switch(2, M1)
    a = advance(s, r, 100)
    assert a.last_cascade is not None and a.last_cascade.time == 100 and a.cascade_count == s.cascade_count + 1
    assert running_mix(a, r) == M1 and a.active == M0 and a.queue == (QueueEntry(SwitchMix(M1), NEVER),)
    assert next_event(a, r) != Event(101, EventKind.READY, len(r.cards), "")


def test_after_a_cascade_no_ready_falls_for_a_queue_switch_that_changes_nothing():
    """"a controlling queue entry whose verb would change the save": the head switches to m0, already active, so the
    cascade at 100 leaves nothing that could act and no READY falls at 101."""
    r, s = _cascading_switch(2, M0)
    a = advance(s, r, 100)
    assert a.last_cascade is not None and a.last_cascade.time == 100
    e = next_event(a, r)
    assert e is None or not (e.time == 101 and e.kind is EventKind.READY), e


def test_invariant_57_need_not_hold_at_a_capped_instant_and_holds_at_the_next():
    """Invariant 57's carve-out: h and r (cap 3 each) land at 100 beside a trigger, five firings, the cap: a ready
    order may wait there. 101 does not hit the cap (two READYs and two taps), and there both lanes are running."""
    r = world(5, capped=3, triggers=[TriggerDef(TriggerId("t"), AfterTime(100), Outcome())])
    s = decide(busy_at_0(r, H, R), r, 0, SetOrders((Order(ALWAYS, TapCard(H)), Order(ALWAYS, TapCard(R)))))
    a = advance(s, r, 100)
    assert a.last_cascade is not None and a.last_cascade.time == 100
    b = advance(a, r, 101)
    assert b.cascade_count == a.cascade_count
    assert (lane(b, HANDS).card, lane(b, RACK).card) == (H, R)


# ---- shipping: an old build's save runs forward, unchanged until it next evaluates --------------------------------

def test_an_old_builds_save_with_a_ready_order_unapplied_waits_for_the_next_evaluating_instant():
    """"Shipping the evaluation change": a stored save standing at an instant with a ready order left unapplied (as
    the old build wrote one) loads as it is and stays so until the next instant that evaluates, here a trigger at 50."""
    r = world(triggers=[TriggerDef(TriggerId("t"), AfterTime(50), Outcome())])
    old = replace(new_save(r), orders=(Order(ALWAYS, TapCard(R)),), latches=(True,))
    s = decode(encode(old, r), r)
    assert s == old
    assert lane(advance(s, r, 49), RACK).card is None
    assert lane(advance(s, r, 50), RACK).card == R


# ---- invariant 57 over random worlds ------------------------------------------------------------------------------

def can_act(s: Save, r: Rules, c: CardId) -> bool:
    """A TapCard of c can act in s: its lane is free and the player's own tap of it starts it now. On a free lane the
    player's tap raises for a locked, unknown, completed or retired card and speed 0, and is a failed tap (nothing
    starts) when unready (DESIGN.txt, "Failed tap"), so it starting is exactly "unlocked, not completed or retired,
    blocker None, speed above 0". The lane is read apart because a player's tap may cut in on a busy one ("CUT-IN",
    "CURE CUT-IN"), which an order's never does."""
    d = next((x for x in r.cards if x.id == c), None)
    if d is None or lane(s, d.lane).card is not None:
        return False
    try:
        t = decide(s, r, s.time, TapCard(c))
    except InvalidVerbError:
        return False
    return lane(t, d.lane).card == c


def queue_breaks_57(s: Save, r: Rules) -> bool:
    """While no order's mix runs, the controlling queue entry (the first whose verb is not dead: a tap of a completed
    card, a switch to a greyed mix) is a TapCard that can act, or a switch to a saved mix that is not running. An entry
    naming an unknown card or a mix not saved stops the check (False): whether it is dead is not stated."""
    v = view(s, r)
    if v.mix_order is not None:
        return False
    completed = {c.card for c in v.completed}
    known = {c.id for c in r.cards}
    saved = {m.id for m in s.mixes}
    for e in s.queue:
        verb = e.verb
        if isinstance(verb, TapCard):
            if verb.card not in known:
                return False
            if verb.card in completed:
                continue
            return can_act(s, r, verb.card)
        if not isinstance(verb, SwitchMix):
            return False   # an answer: these worlds hold no offers, so the check stops as for an unknown verb
        if verb.mix not in saved:
            return False
        if verb.mix in v.greyed_mixes:
            continue
        return verb.mix != v.running_mix
    return False


def breaks_57(s: Save, r: Rules) -> str | None:
    """What in s breaks invariant 57, or None; None also at an instant that hit the firing cap (the carve-out)."""
    if s.last_cascade is not None and s.last_cascade.time == s.time:
        return None
    for i, (o, on) in enumerate(zip(s.orders, s.latches)):
        if on and isinstance(o.then, TapCard) and can_act(s, r, o.then.card):
            return f"order {i} {o.then.card} can act at {s.time}"
    return f"queue head can act at {s.time}" if queue_breaks_57(s, r) else None


def test_the_57_check_holds_a_true_order_on_a_busy_lane_to_wait_even_for_a_cure():
    """Invariant 57's "its lane free", against "CURE CUT-IN": "An order's cure does not cut in; it waits for the task to
    land". h holds the hands from the SetOrders at 0 while "full" shows and cu, a cure for it, has a true order: the
    player could cut in with cu, yet no order can act. The control, the same orders by hand with the hands free, is
    reported."""
    cu, full = CardId("cu"), ChipId("full")
    r = rules([StoreDef(X, 100 * Q, 0), StoreDef(W, 100 * Q, 3 * Q)],
              cards=[CardDef(H, 100), CardDef(cu, 100, inputs=(Amount(W, Q),))],
              chips=[ChipDef(full, AtLeast(StoreValue(W), 2 * Q, 2 * Q), ())])
    orders = (Order(ALWAYS, TapCard(H)), Order(ALWAYS, TapCard(cu)))
    assert breaks_57(replace(new_save(r), orders=orders, latches=(True, True)), r) is not None
    s = decide(new_save(r), r, 0, SetOrders(orders))
    assert lane(s, HANDS).card == H and view_of(s, r, cu).cuts_in
    for t in (0, 1, 99):
        assert breaks_57(advance(s, r, t), r) is None, t


Steps = tuple[tuple[int, Verb | None], ...]
Case = tuple[Rules, tuple[Modifier, ...], Steps]


def _two_lanes(sc: Scenario) -> bool:
    return len({c.lane for c in sc.rules.cards}) > 1


@st.composite
def driven_st(draw: st.DrawFn, two_lanes: bool) -> Case:
    """A cards scenario (with cards on both lanes when `two_lanes`) with an always-true tap order on every card and up to
    two orders on any condition, in any sequence, a queue, and its later steps with the player's SwitchMix and SaveMix replaced by a plain advance:
    invariant 57 is stated for saves reached without those. The setup's own SaveMix and SwitchMix come first, and
    SetOrders and SetQueue evaluate after them."""
    sc = draw(scenario_st().filter(_two_lanes) if two_lanes else scenario_st())
    r = sc.rules
    always = [Order(ALWAYS, TapCard(c.id)) for c in r.cards]
    extra = draw(st.lists(st.builds(Order, condition_st(r), order_verb_st(r)), max_size=2))
    orders = draw(st.permutations(always + extra))
    queue = draw(st.lists(st.builds(QueueEntry, order_verb_st(r), condition_st(r)), max_size=3))
    setup = sc.steps[:3]
    rest: list[tuple[int, Verb | None]] = [
        (dt, None if isinstance(v, (SaveMix, SwitchMix)) else v) for dt, v in sc.steps[3:]]
    tail = (0, SetOrders(tuple(orders))), (draw(st.integers(0, span(r, 300))), SetQueue(tuple(queue)))
    return r, sc.modifiers, (*setup, *tail, *rest, (draw(st.integers(0, span(r, 6000))), None))


@few(4)
@given(driven_st(two_lanes=True))
def test_invariant_57_both_lanes_driven(case: Case):
    """Invariant 57 on worlds with cards on both lanes, the costly kind: its 7 examples run as two tests of 4 and 3, and
    the any-world 7 as a third, so each stays inside the per-test ceiling (tests/conftest.py)."""
    check_57(case)


@few(3)
@given(driven_st(two_lanes=True))
def test_invariant_57_both_lanes_driven_more(case: Case):
    """The other 3 of the both-lanes examples (Hypothesis seeds each test by its name, so these differ)."""
    check_57(case)


@few(7)
@given(driven_st(two_lanes=False))
def test_invariant_57_every_lane_driven(case: Case):
    """Invariant 57 on any world."""
    check_57(case)


def check_57(case: Case) -> None:
    """Invariant 57: after each evaluating step, and at the next few events and +/- 1 second after the last, no true
    tap order's card and no controlling queue verb can act, except at an instant that hit the firing cap."""
    r, mods, steps = case
    validate_rules(r)
    s = new_save(r, mods)
    for k, (dt, verb) in enumerate(steps):
        t = s.time + dt
        s = advance(s, r, t) if verb is None else try_decide(s, r, t, verb)
        if k >= 3:
            assert breaks_57(s, r) is None, breaks_57(s, r)
    for later in timeline(s, r, (span(r, 3000),), events=3):
        assert breaks_57(later, r) is None, breaks_57(later, r)
