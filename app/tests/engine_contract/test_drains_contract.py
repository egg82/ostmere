"""Drains, part one: a take forgiven at 0 (engine DESIGN.txt, "DRAINS", invariants 121-124). Written blind from that part
and the public interface; MUTANTS_drains.txt names the wrong implementations each test must turn red for (the `kills`
marker). The default cure is drains_world's: 10 items of x per completion of 100 s, 360_000 units a second at full
speed, so every expected number is exact."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AtLeast, CardCount, EventKind, Flow, FlowKind,
    LineKey, Modifier, ModifierKind, Order, QueueEntry, RateRef, RunBy, RunKind, SetOrders, SetQueue, SourceId,
    StandingDef, StoreValue, TapCard, WorkRef, advance, advance_logged, decide_logged, new_save, next_event,
    per_hour, segment, xp,
)
from drains_world import BIG, CURE, D, F, I, K, PER_SECOND, X, X2, Y, at, card_view, cure, drained, kills, mixed, near
from drains_world import tapped, world

DONE, FAILED = LineKey("cure.done"), LineKey("cure.failed")
SAMPLES = (0, 1, 2, 10, 39, 40, 41, 50, 99, 100, 101, 500)
TRICKLE = StandingDef(ActionId("trickle"), makes=(Flow(X, per_hour(1)),))
"""x rises 1000 units a second: above 0 from the first second."""


@kills(1, 3, 4, 5)
@pytest.mark.parametrize("x0", [4 * Q, 10 * Q, 1, 9 * Q + 1])
def test_a_tap_with_less_than_the_whole_take_lands_at_its_usual_time_with_the_store_at_zero(x0: int):
    """Invariants 122, 124: started with 0 < x <= A' the tap is never interrupted, lands at start + its usual time, and x
    follows max(0, x0 - A' * work / (work_s * BP)) from the start to the landing and after."""
    r = world(cure(lines=(DONE,)), x0=x0)
    s = tapped(r)
    assert [ln.key for ln in advance_logged(s, r, 99).lines] == [] and advance(s, r, 99).lanes[0].card == CURE
    landed = advance_logged(s, r, 100)
    assert [(ln.time, ln.key, ln.card) for ln in landed.lines] == [(100, DONE, CURE)]
    assert landed.save.lanes[0].card is None
    for t in SAMPLES:
        v = at(s, r, X, t)
        assert v >= 0, t
        near(v, drained(x0, 10 * Q, 100, BP * min(t, 100)))


@kills(3)
def test_the_store_reaching_zero_is_an_event_and_stays_at_zero_between_events():
    """Invariant 16 and the DRAINS part: reaching 0 is a STORE_LIMIT event; from it the segment is flat at 0."""
    r = world(cure(), x0=4 * Q)
    s = tapped(r)
    ev = next_event(s, r)
    assert ev is not None and (ev.time, ev.kind, ev.subject) == (40, EventKind.STORE_LIMIT, str(X))
    assert segment(s, r, X).rate == -D
    for t in (40, 41, 70):
        flat = segment(advance(s, r, t), r, X)
        assert (flat.start_value, flat.rate) == (0, 0), t


@kills(3, 4)
def test_a_remainder_below_the_drain_is_forgiven_and_never_paid_back():
    """Invariants 122, 127: an inflow n below the drain d keeps x at 0 (the drain takes n, the rest is forgiven); x is
    exact until the second it would go below 0, then 0 until the landing, then rises at n alone."""
    n = per_hour(100)
    r = world(cure(), x0=4 * Q, standing=(StandingDef(ActionId("src"), makes=(Flow(X, n),)),))
    s = tapped(r)
    assert at(s, r, X, 55) == 4 * Q - (D - n) * 55
    assert [at(s, r, X, t) for t in (56, 57, 80, 99, 100)] == [0] * 5
    assert at(s, r, X, 110) == 10 * n


@kills(5)
@pytest.mark.parametrize("mods,taken", [
    ((), 10 * Q),
    ((Modifier(RateRef(CURE, FlowKind.COST, X), ModifierKind.MUL_BP, 15_000, SourceId("m")),), 15 * Q),
    ((Modifier(RateRef(CURE, FlowKind.COST, X), ModifierKind.ADD_BP, -5_000, SourceId("m")),), 5 * Q),
    ((Modifier(RateRef(CURE, FlowKind.MAKE, Y), ModifierKind.MUL_BP, 30_000, SourceId("m")),), 10 * Q),
    ((Modifier(WorkRef(CURE), ModifierKind.MUL_BP, 20_000, SourceId("m")),), 10 * Q),
], ids=["plain", "cost x1.5", "cost -50%", "other line", "work x2"])
def test_a_completion_takes_its_amount_under_the_modifiers_aimed_at_its_cost_line_alone(
        mods: tuple[Modifier, ...], taken: int):
    """Invariant 122: one completion takes A' (the quantity under the entries aimed at RateRef(card, COST, x) alone), at
    any work speed; a tap that has landed takes nothing more."""
    r = world(cure(makes=(Flow(Y, PER_SECOND),)), x0=BIG)
    s = tapped(r, mods)
    t = 50 if mods and isinstance(mods[0].target, WorkRef) else 100
    assert at(s, r, X, t) == BIG - taken
    assert at(s, r, X, 3 * t) == BIG - taken, "the card has landed: nothing keeps taking"


@kills(5)
@pytest.mark.parametrize("share_bp,per_completion_s", [(BP, 100), (5_000, 200), (2_500, 400)])
def test_a_mixed_card_takes_its_amount_per_completion_at_any_share(share_bp: int, per_completion_s: int):
    r = world(cure(), x0=BIG)
    s = mixed(r, share_bp)
    for k in (1, 2, 3):
        assert at(s, r, X, k * per_completion_s) == BIG - k * 10 * Q


@kills(5)
def test_a_rounded_up_take_is_charged_once_per_completion():
    """Invariant 122: the quantity under the modifiers is rounded up once (7 units x 50% is 3.5, so 4 a completion); the
    store follows the exact rational to under a unit and is exact at each completion."""
    mods = (Modifier(RateRef(CURE, FlowKind.COST, X), ModifierKind.MUL_BP, 5_000, SourceId("m")),)
    r = world(cure(7, work_s=3), x0=10**6)
    s = mixed(r, BP, mods)
    for t in (3, 6, 300, 3000):
        assert at(s, r, X, t) == 10**6 - 4 * (t // 3), t


@kills(5)
@pytest.mark.parametrize("a,work_s", [(7, 3), (1, 7), (5 * Q + 1, 61)])
def test_the_store_follows_the_exact_rational_for_odd_amounts(a: int, work_s: int):
    x0 = 10**9
    r = world(cure(a, work_s=work_s), x0=x0)
    s = mixed(r)
    for t in (1, 2, work_s - 1, work_s, work_s + 1, 5 * work_s, 997):
        near(at(s, r, X, t), drained(x0, a, work_s, BP * t))
        if t % work_s == 0:
            assert at(s, r, X, t) == x0 - a * (t // work_s), t


@kills(1, 2)
@pytest.mark.parametrize("x0", [0, 4 * Q])
@pytest.mark.parametrize("share_bp", [BP, 5_000])
def test_a_mixed_card_keeps_running_with_its_drain_store_at_zero(x0: int, share_bp: int):
    """Invariant 121: never paused, interrupted or WAITING because of a drain: its work, makes and XP run at its share
    whether the store is above 0, reaching 0 or at 0."""
    r = world(cure(skill=K, xp_per_hour=PER_SECOND, makes=(Flow(Y, PER_SECOND),)), x0=x0)
    s = mixed(r, share_bp)
    make = PER_SECOND * share_bp // BP
    last_xp = -1
    for t in (1, 39, 40, 41, 79, 80, 81, 100, 250):
        a = advance(s, r, t)
        cv = card_view(a, r)
        assert (a.pauses, cv.run, cv.by) == ((), RunKind.FULL, RunBy.MIX), t
        assert at(s, r, Y, t) == make * t, t
        assert xp(s, r, K, t) > last_xp, t
        last_xp = xp(s, r, K, t)
        assert cv.completions == t * share_bp // (100 * BP), t
        near(at(s, r, X, t), drained(x0, 10 * Q, 100, share_bp * t))


@kills(1)
def test_a_tap_with_the_store_hitting_zero_midway_keeps_its_lane_and_its_work():
    r = world(cure(makes=(Flow(Y, PER_SECOND),)), x0=4 * Q)
    s = tapped(r)
    for t in (39, 40, 41, 99):
        a = advance(s, r, t)
        assert a.lanes[0].card == CURE and a.pauses == (), t
        assert at(s, r, Y, t) == t * Q, t
        assert card_view(a, r).by == RunBy.TAP, t


# ---- 123: ready above 0 -------------------------------------------------------------------------------------

@kills(6)
def test_a_players_tap_with_the_drain_store_at_zero_is_a_failed_tap():
    """Invariant 123 (and 22): failed == the card, the save only advanced, the failed line emitted, the blocker
    AtLeast(StoreValue(x), 1, 1) with no ready_at while nothing raises x."""
    r = world(cure(failed_line=FAILED), x0=0)
    s0 = new_save(r)
    step = decide_logged(s0, r, 5, TapCard(CURE))
    assert step.failed == CURE and step.save == advance(s0, r, 5)
    assert [(ln.key, ln.card) for ln in step.lines] == [(FAILED, CURE)] and step.save.lanes[0].card is None
    blocker = card_view(step.save, r).blocker
    assert blocker is not None and blocker.condition == AtLeast(StoreValue(X), 1, 1) and blocker.ready_at is None


@kills(6)
def test_the_blocker_has_a_ready_time_when_something_raises_the_store():
    r = world(cure(), x0=0, standing=(TRICKLE,))
    blocker = card_view(new_save(r), r).blocker
    assert blocker is not None and blocker.condition == AtLeast(StoreValue(X), 1, 1) and blocker.ready_at == 1


@kills(6, 7)
def test_a_tap_with_one_unit_in_the_store_starts_and_takes_nothing_at_its_start():
    """Invariant 123: x at 1 unit or more starts, and x is unchanged at the start instant (no lump at the start)."""
    r = world(cure(failed_line=FAILED), x0=1)
    step = decide_logged(new_save(r), r, 0, TapCard(CURE))
    assert step.failed is None and step.lines == () and step.save.lanes[0].card == CURE
    assert card_view(step.save, r).blocker is None
    assert at(step.save, r, X, 0) == 1 and at(step.save, r, X, 1) == 0


@kills(7)
def test_a_tap_at_a_low_level_pays_by_its_work_not_at_once():
    r = world(cure(), x0=4 * Q)
    s = tapped(r)
    assert at(s, r, X, 0) == 4 * Q and at(s, r, X, 1) == 4 * Q - D


@kills(6)
@pytest.mark.parametrize("verb", ["order", "queue"])
def test_an_order_or_queue_entry_naming_it_waits_for_the_store_to_exceed_zero_then_starts_it(verb: str):
    """Invariant 123 (and 23): at 0 nothing changes and no failed tap is made; READY falls when x first exceeds 0, and the
    card starts then with x unchanged at that instant."""
    r = world(cure(failed_line=FAILED), x0=0, standing=(TRICKLE,))
    if verb == "order":
        v = SetOrders((Order(AfterTime(0), TapCard(CURE)),))
    else:
        v = SetQueue((QueueEntry(TapCard(CURE), AtLeast(CardCount(CURE), 1, 1)),))
    step = decide_logged(new_save(r), r, 0, v)
    s = step.save
    assert step.lines == () and s.lanes[0].card is None
    ev = next_event(s, r)
    assert ev is not None and (ev.time, ev.kind) == (1, EventKind.READY)
    assert advance(s, r, 0).lanes[0].card is None
    started = advance(s, r, 1)
    assert started.lanes[0].card == CURE and at(started, r, X, 1) == 1000
    assert advance_logged(s, r, 1).lines == ()


# ---- the blocker's order ----------------------------------------------------------------------------------

@kills(17)
@pytest.mark.parametrize("x0,x2,i0,f0,expected", [
    (0, 0, 4 * Q, 0, AtLeast(StoreValue(I), 10 * Q, 10 * Q)),
    (0, 0, 10 * Q, 0, AtLeast(StoreValue(X), 1, 1)),
    (Q, 0, 10 * Q, 0, AtLeast(StoreValue(X2), 1, 1)),
    (Q, Q, 10 * Q, 0, AtLeast(StoreValue(F), 5 * Q, 5 * Q)),
], ids=["input first", "then the first drain", "then the next drain", "then requires"])
def test_the_blocker_reads_inputs_then_drains_in_order_then_requires_and_a_drain_asks_for_one_unit(
        x0: int, x2: int, i0: int, f0: int, expected: AtLeast):
    card = cure(inputs=(Amount(I, 10 * Q),), requires=(AtLeast(StoreValue(F), 5 * Q, 5 * Q),),
                drains=(Amount(X, 10 * Q), Amount(X2, 10 * Q)))
    r = world(card, x0=x0, x2=x2, i0=i0)
    blocker = card_view(new_save(r), r).blocker
    assert blocker is not None and blocker.condition == expected
    step = decide_logged(new_save(r), r, 0, TapCard(CURE))
    assert step.failed == CURE and step.save.lanes[0].card is None
