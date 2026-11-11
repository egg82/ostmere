"""Invariants 12-14: same-instant ordering, the cascade cap, hysteresis and exact latch events."""
from hypothesis import example, given, strategies as st

import pytest

from ashfall_app.engine import (
    BP, CardShare, Pause, AfterTime, AtLeast, AtMost, EngineError, Event, EventKind, Flow, Mix, Order, QueueEntry,
    Rules, Running, Save, SaveMix, SetOrders, SetQueue, SkillLevel, StoreDef, StoreValue, SwitchMix, advance, decide, level,
    new_save, next_event, value, view,
)
from contract_gen import Q, SK, card, card_id, make_rules, mix_id, probe_times, scenario_st, store_id, few, Scenario


def _tied_world(n: int, hours: int, rate: int, reverse: bool = False, max_firings: int = 1000):
    """n stores, each drained by its own card, all emptying at the same instant (n in 2, 4: shares are exact)."""
    share = BP // n
    eff = rate  # base*share*BP/BP^2 with base = rate*n is exactly rate
    stores = [StoreDef(store_id(i), Q * hours, Q * hours) for i in range(n)]
    acts = [card(i, 0, (), (Flow(store_id(i), rate * n),)) for i in range(n)]
    if reverse:
        stores.reverse()
        acts.reverse()
    rules = make_rules(stores, acts, max_firings=max_firings)
    on = Mix(mix_id(0), tuple(CardShare(card_id(i), share) for i in range(n)))
    s = decide(new_save(rules), rules, 0, SaveMix(on))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    return rules, s, -(-(Q * hours) // eff)


@given(n=st.sampled_from([2, 4]), hours=st.integers(1, 5), rate=st.integers(1, 3000), rev=st.booleans())
def test_tied_stores_resolve_in_rules_order(n: int, hours: int, rate: int, rev: bool):
    """Invariant 12 (same-instant order): stores emptying at one instant resolve lowest sequence (rules index)
    first; reversing the rules' order changes only which store wins the tie."""
    rules, s, T = _tied_world(n, hours, rate, rev)
    first = rules.stores[0].id
    assert next_event(s, rules) == Event(T, EventKind.STORE_LIMIT, 0, first)


@given(n=st.sampled_from([2, 4]), hours=st.integers(1, 5), rate=st.integers(1, 3000), probe=st.integers(0, 40_000))
def test_swapping_rules_order_changes_no_values(n: int, hours: int, rate: int, probe: int):
    """Invariant 12 (same-instant order): the same world with stores/cards listed in reverse order has the same
    event times and the same value for every store id at every time."""
    r1, s1, T = _tied_world(n, hours, rate, False)
    r2, s2, _ = _tied_world(n, hours, rate, True)
    for t in (0, T - 1, T, T + 1, probe):
        for i in range(n):
            assert value(s1, r1, store_id(i), t) == value(s2, r2, store_id(i), t)
    e1, e2 = next_event(s1, r1), next_event(s2, r2)
    assert e1 is not None and e2 is not None and e1.time == e2.time == T


@given(hours=st.integers(1, 5), rate=st.integers(1, 3000))
def test_store_limit_resolves_before_level_up(hours: int, rate: int):
    """Invariant 12 (same-instant order): a store emptying and a skill levelling at one instant: kind STORE_LIMIT
    (0) comes before LEVEL_UP (4); the level-up still lands at that instant."""
    v = Q * hours
    # one card drains `rate`/h at 100% and trains XP at the same rate: both events fall at ceil(v / rate)
    rules = make_rules([StoreDef(store_id(0), v, v)], [card(0, rate, (), (Flow(store_id(0), rate),))],
                       thresholds=(v, 2 * v))
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(mix_id(0), (CardShare(card_id(0), BP),))))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    e = next_event(s, rules)
    assert e is not None and e == Event(-(-v // rate), EventKind.STORE_LIMIT, 0, "s0")
    assert level(s, rules, SK, e.time) == 2


LATE = 10**8  # an instant long after any cascade the test builds
ORDERS = (Order(AtMost(StoreValue(store_id(0)), 0, 0), SwitchMix(mix_id(1))),
          Order(AfterTime(LATE), SwitchMix(mix_id(0))))


@example(n=3, hours=1, rate=1, cap=2, after=1)
@example(n=2, hours=1, rate=1, cap=2, after=1)
@given(n=st.sampled_from([2, 3, 4]), hours=st.integers(1, 3), rate=st.integers(1, 2000), cap=st.integers(1, 4),
       after=st.integers(1, 5000))
def test_cascade_cap_suspends_orders_and_never_raises(n: int, hours: int, rate: int, cap: int, after: int):
    """Invariants 13, 1 (cascade cap, split): n+1 firings at instant T with a smaller cap: no error, cascade_count
    rises by one and last_cascade is CascadeLimit(T, >= cap), the order's latch change waits past the cap at T, so its
    mix does not run (a control with a high cap does run it), it is seen at the next latch change (the order's mix
    then runs), a player's decide() at T starts a fresh count (its SetOrders sets the latch), splitting across T
    changes nothing, and no order ever changes the player's own mix."""
    cap = min(cap, n)
    rate = 2 * rate  # keep rates even so shares are exact for n in 2, 4; for 3 use a rate divisor below
    results: dict[int, tuple[Rules, Save]] = {}
    for mf in (cap, 1000):
        stores = [StoreDef(store_id(i), Q * hours, Q * hours) for i in range(n)]
        acts = [card(i, 0, (), (Flow(store_id(i), rate),)) for i in range(n)]
        rules = make_rules(stores, acts, max_firings=mf)
        # every card at 10000/n bp; a card's effective rate is then rate*(10000//n)/10000, so T is read off
        # the engine's own first event rather than recomputed
        on = Mix(mix_id(0), tuple(CardShare(card_id(i), BP // n) for i in range(n)))
        off = Mix(mix_id(1), ())
        s = new_save(rules)
        for v in (SaveMix(on), SaveMix(off), SwitchMix(mix_id(0)),
                  SetOrders(ORDERS)):
            s = decide(s, rules, 0, v)
        results[mf] = (rules, s)
    r_cap, s_cap = results[cap]
    r_hi, s_hi = results[1000]
    hi, capped = next_event(s_hi, r_hi), next_event(s_cap, r_cap)
    assert hi is not None and capped is not None
    T = hi.time
    assert capped.time == T
    ctrl = advance(s_hi, r_hi, T)
    assert view(ctrl, r_hi).running_mix == mix_id(1) and ctrl.cascade_count == 0 and ctrl.last_cascade is None
    hit = advance(s_cap, r_cap, T)
    assert view(hit, r_cap).running_mix == mix_id(0)  # the mix order's latch waits past the cap at T
    assert ctrl.active == hit.active == mix_id(0)
    assert hit.cascade_count == s_cap.cascade_count + 1
    assert hit.last_cascade is not None and hit.last_cascade.time == T and hit.last_cascade.firings >= cap
    later = advance(hit, r_cap, T + after)
    assert later.time == T + after and later.cascade_count == hit.cascade_count
    if cap >= 2:  # with cap 1 the latch event alone reaches the cap, so no verb can ever follow an event
        resumed = advance(hit, r_cap, LATE)  # the AfterTime latch changes, the empty-store order's is seen and wins
        assert view(resumed, r_cap).running_mix == mix_id(1) and resumed.active == mix_id(0)
    fresh = decide(hit, r_cap, T, SetOrders(ORDERS))  # the cap stops chains, not the player
    assert view(fresh, r_cap).running_mix == mix_id(1)
    for split in (T - 1, T, T + 1):
        assert advance(advance(s_cap, r_cap, split), r_cap, T + after) == advance(s_cap, r_cap, T + after)


@pytest.mark.parametrize("cap", range(1, 10))
def test_every_latch_change_is_a_firing_and_a_mix_orders_waits_past_the_cap(cap: int):
    """Invariant 13 (cascade cap) with Order mix: "each event processed ... is one firing", and past the cap a
    SwitchMix order's latch change waits. Two orders flip a mix on and off by what runs (Running is read plainly): the
    first order's mix stops c, which releases it, so the player's mix runs c again, which raises it. No verb is applied
    (an order's mix runs while latched), so every firing is one latch change of the first order; the chain stops at
    the cap, with the first order latched after an even count, and the player's mix never changes."""
    c = card(0, 0, (Flow(store_id(0), 1000),), ())
    rules = make_rules([StoreDef(store_id(0), 10 * Q, 0)], [c], max_firings=cap)
    run, stop = mix_id(0), mix_id(1)
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(run, (CardShare(c.id, BP),))))
    s = decide(decide(s, rules, 0, SaveMix(Mix(stop, ()))), rules, 0, SwitchMix(run))
    orders = (Order(AtLeast(Running(c.id), 1, 1), SwitchMix(stop)), Order(AtMost(Running(c.id), 0, 0), SwitchMix(run)))
    s = decide(s, rules, 0, SetOrders(orders))
    assert s.active == run
    assert view(s, rules).running_mix == (stop if cap % 2 == 0 else run)
    assert s.cascade_count == 1 and s.last_cascade is not None
    assert (s.last_cascade.time, s.last_cascade.firings) == (0, cap)


@pytest.mark.parametrize("cap", range(2, 7))
def test_a_run_of_queue_mixes_pops_whole_past_the_firing_cap(cap: int):
    """Invariant 13 (cascade cap), "Queue mix": a queue's switch changes nothing when applied, and its pops still
    resolve past the cap. A queue alternates two switches, each popping once what runs flips (a switch to
    `run` pops once c runs, one to `stop` once it does not): all twelve pop at the one instant, which counts as a
    cascade, and the run ends because each pop shortens the queue."""
    c = card(0, 0, (Flow(store_id(0), 1000),), ())
    rules = make_rules([StoreDef(store_id(0), 10 * Q, 0)], [c], max_firings=cap)
    run, stop = mix_id(0), mix_id(1)
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(run, (CardShare(c.id, BP),))))
    s = decide(decide(s, rules, 0, SaveMix(Mix(stop, ()))), rules, 0, SwitchMix(stop))
    pair = (QueueEntry(SwitchMix(run), AtLeast(Running(c.id), 1, 1)),
            QueueEntry(SwitchMix(stop), AtMost(Running(c.id), 0, 0)))
    s = decide(s, rules, 0, SetQueue(pair * 6))
    assert s.queue == ()
    assert s.cascade_count == 1 and s.last_cascade is not None and s.last_cascade.time == 0


@few(10)
@given(sc=scenario_st(max_firings=None))
def test_fuzzed_orders_never_raise_or_stall(sc: Scenario):
    """Invariant 13 (cascade cap): random rules, orders and queues with small firing caps: advance never raises an
    EngineError, always reaches the requested time, and records each capped instant once, in time order."""
    from contract_gen import play
    try:
        s = play(sc)
        for t in probe_times(s, sc.rules, sc.offsets):
            a = advance(s, sc.rules, t)
            assert a.time == t
            assert a.cascade_count >= s.cascade_count >= 0
            assert (a.last_cascade is None) == (a.cascade_count == 0)
            if a.last_cascade is not None:
                assert a.last_cascade.time <= t and a.last_cascade.firings >= sc.rules.max_firings_per_instant
    except EngineError as err:  # pragma: no cover - the property failing is the point
        raise AssertionError(f"valid input raised {type(err).__name__}") from err


def _band_world(lo: int, hi: int, up: int, down: int):
    """A store oscillating between two orders with a hysteresis band: reaching `hi` switches to the draining mix,
    reaching `lo` switches back to the filling mix; each order's latch releases at the other order's threshold."""
    rules = make_rules(
        [StoreDef(store_id(0), 10 * Q, 5 * Q)],
        [card(0, 0, (Flow(store_id(0), up),), ()),
         card(1, 0, (), (Flow(store_id(0), down),))])
    mixes = [Mix(mix_id(0), (CardShare(card_id(0), BP),)), Mix(mix_id(1), (CardShare(card_id(1), BP),))]
    orders = (Order(AtLeast(StoreValue(store_id(0)), hi, lo), SwitchMix(mix_id(1))),
              Order(AtMost(StoreValue(store_id(0)), lo, hi), SwitchMix(mix_id(0))))
    s = new_save(rules)
    for v in (SaveMix(mixes[0]), SaveMix(mixes[1]), SwitchMix(mix_id(0)), SetOrders(orders)):
        s = decide(s, rules, 0, v)
    return rules, s, orders


@few(10)
@given(lo=st.integers(1, 3), hi=st.integers(7, 9), up=st.integers(300, 4000), down=st.integers(300, 4000))
def test_hysteresis_latches_flip_exactly_at_the_band_edges(lo: int, hi: int, up: int, down: int):
    """Invariants 14, 8 (hysteresis, exact event times): with release < value an AtLeast latch rises at the first
    second the store is >= value and falls only at the first second it is < release; so it cannot fire twice
    without the subject crossing the band twice. Mirror for AtMost."""
    lo, hi = lo * Q, hi * Q
    rules, s, _ = _band_world(lo, hi, up, down)
    x = store_id(0)
    for _ in range(14):
        e = next_event(s, rules)
        if e is None:
            break
        n = advance(s, rules, e.time)
        for i, (before, after) in enumerate(zip(s.latches, n.latches)):
            if before == after:
                continue
            v_now, v_prev = value(s, rules, x, e.time), value(s, rules, x, e.time - 1)
            if i == 0 and after:
                assert v_now >= hi and v_prev < hi
            if i == 0 and not after:
                assert v_now < lo and v_prev >= lo
            if i == 1 and after:
                assert v_now <= lo and v_prev > lo
            if i == 1 and not after:
                assert v_now > hi and v_prev <= hi
        s = n


_HELD_MIX_LATCH = Scenario(
    make_rules([StoreDef(store_id(0), 10 * Q, 0)], [card(0, 237)], thresholds=(169, 340), max_firings=1), (),
    ((0, SaveMix(Mix(mix_id(0), ()))), (0, SaveMix(Mix(mix_id(1), (CardShare(card_id(0), BP),)))), (0, SwitchMix(mix_id(1))),
     (0, SetOrders((Order(AtLeast(SkillLevel(SK), 2, 1), SwitchMix(mix_id(0))),)))),
    SwitchMix(mix_id(1)), (1,))
"""A cap of one firing: k0 reaches level 2 at 1 by a LEVEL_UP, which is the instant's one firing, so the mix order's
latch change past it waits (DESIGN.txt, "Firing cap")."""


def _definition(a: Save, rules: Rules, c: AfterTime | AtLeast | AtMost) -> bool | None:
    """What invariant 14 says c's latch is at a: True past `value`, False past `release` the other way, None in the
    band (it keeps its state); AfterTime is exactly now >= time."""
    if isinstance(c, AfterTime):
        return a.time >= c.time
    subj = c.subject
    if isinstance(subj, StoreValue):
        v = value(a, rules, subj.store, a.time)
    else:
        assert isinstance(subj, SkillLevel)
        v = level(a, rules, subj.skill, a.time)
    if isinstance(c, AtLeast):
        return True if v >= c.value else False if v < c.release else None
    return True if v <= c.value else False if v > c.release else None


@few(10)
@given(sc=scenario_st())
@example(sc=_HELD_MIX_LATCH)
def test_latch_state_matches_its_definition(sc: Scenario):
    """Invariants 14, 13: at every resolved save a latch is what _definition says, or keeps its state in the band. The
    one exception is the cap's: past the firing cap a mix order's latch change waits for the next instant where
    something else fires (DESIGN.txt, "Firing cap"), so a mix order's latch may disagree only when the last cascade
    reached the cap and, if it came after the played save, the latch already disagreed the same way there."""
    from contract_gen import play
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        for o, latch in zip(a.orders, a.latches):
            want = _definition(a, sc.rules, o.when)
            if want is None or latch == want:
                continue
            held = a.last_cascade
            assert isinstance(o.then, SwitchMix) and held is not None, (t, o)
            assert held.firings >= sc.rules.max_firings_per_instant, (t, o, held)
            if held.time >= s.time:
                assert _definition(advance(s, sc.rules, held.time), sc.rules, o.when) == want, (t, o, held)


@given(r0=st.integers(1, 400), r1=st.integers(1, 400), swap=st.booleans())
def test_tied_store_limits_resolve_in_rules_order_observably(r0: int, r1: int, swap: bool):
    """Invariant 12 (same-instant order): one card costs two stores that run dry at the same instant. Events
    resolve in sequence order, so the pause is attributed to the store listed first in rules (and resumes at an
    hour of THAT store's cost); listing the stores the other way round moves the attribution, nothing else."""
    T = 3600
    stores = [StoreDef(store_id(0), 50 * Q, r0 * T), StoreDef(store_id(1), 50 * Q, r1 * T)]
    flows = [Flow(store_id(0), r0), Flow(store_id(1), r1)]
    if swap:
        stores.reverse()
        flows.reverse()
    rules = make_rules(stores, [card(0, 0, (), tuple(flows))])
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(mix_id(0), (CardShare(card_id(0), BP),))))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    a = advance(s, rules, T)
    first = rules.stores[0].id
    cost = next(f.per_hour for f in flows if f.store == first)
    assert a.pauses == (Pause(card_id(0), first, min(50 * Q, 3600 * cost)),)
    assert all(value(a, rules, sd.id, T + 5) == 0 for sd in rules.stores)
