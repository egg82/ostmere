"""Invariants 92 and 93 (engine DESIGN.txt, "THE TOWN'S MIX": "Running town mix", "Verbs", "Rates on a joined lane",
"Join"): which town mix runs is set per layer by the always rule's pushdown; a tap order on a joined lane acts as it
would if the lane ran no shares; a repeat-eligible card tapped by an always rule and the same card at BP in the running
town mix give the same stores, work and counts."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, Order, Outcome, RunKind, Rules, Save, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind,
    advance, decide, view,
)
from town_mix_world import (
    A1, A2, AC, ALWAYS, B1, B2, C1, HM1, HM2, LA, LB, LC, TM, TM2, V, WORK, X, Y, always, card_view, count, hands_mixes, joiner, lane_card,
    orders, start, stored, work_done, world,
)

TWO = (joiner("ja", LA, TM, A1), joiner("jb", LB, TM2, B1))
"""la joins town:main with a1, lb joins town:two with b1: two town mixes, each person in one."""


def _two_town_mixes():
    r = world(TWO)
    return r, start(r)


def test_the_first_latched_town_order_names_the_running_town_mix():
    """Invariant 92(a): the joins appended town:main's rule then town:two's, so town:main runs, at order 0; with
    nothing latched nobody runs shares."""
    r, s = _two_town_mixes()
    v = view(s, r)
    assert (v.running_town_mix, v.town_mix_order) == (TM, 0)
    assert abs(stored(s, r, X, 100) - 100 * Q) <= 100 and stored(s, r, V, 100) == 0
    none = decide(s, r, 0, orders())
    assert view(none, r).running_town_mix is None
    assert stored(none, r, X, 100) == 0 and stored(none, r, V, 100) == 0


def test_order_sequence_is_priority_among_town_orders_and_a_latch_change_switches_the_mix():
    """Invariant 92(a): [from 500: town:two] above [always: town:main]: main runs to 500, two runs from 500."""
    r, s = _two_town_mixes()
    s = decide(s, r, 0, orders(Order(AfterTime(500), SwitchMix(TM2)), Order(ALWAYS, SwitchMix(TM))))
    before, after = view(advance(s, r, 100), r), view(advance(s, r, 600), r)
    assert (before.running_town_mix, before.town_mix_order) == (TM, 1)
    assert (after.running_town_mix, after.town_mix_order) == (TM2, 0)
    assert abs(stored(s, r, X, 1000) - 500 * Q) <= 1000
    assert abs(stored(s, r, V, 1000) - 500 * Q) <= 1000


def test_the_hands_and_the_towns_running_mixes_are_computed_apart():
    """Invariant 92(a): hands orders never change running_town_mix and town orders never change running_mix; the
    hands' mix falls back to save.active, which a town mix never is."""
    r, s = _two_town_mixes()
    s = start(r, *hands_mixes(), SwitchMix(HM1))
    s = decide(s, r, 0, orders(Order(AfterTime(300), SwitchMix(HM2)), Order(ALWAYS, SwitchMix(TM2)),
                               Order(ALWAYS, SwitchMix(TM))))
    early, late = view(advance(s, r, 100), r), view(advance(s, r, 400), r)
    assert (early.running_mix, early.running_town_mix) == (HM1, TM2)
    assert (late.running_mix, late.running_town_mix) == (HM2, TM2)
    assert s.active == HM1
    bare = decide(s, r, 0, orders(Order(ALWAYS, SwitchMix(TM))))
    assert (view(bare, r).running_mix, view(bare, r).running_town_mix) == (HM1, TM)


def _completions(s: Save, r: Rules, t: int) -> int:
    """ac's completions at t: a finished capped card leaves View.cards for View.completed."""
    v = view(advance(s, r, t), r)
    return next((cv.completions for cv in v.cards if cv.card == AC), 1)


def test_a_tap_order_acts_at_the_instants_it_would_if_the_lane_ran_no_shares():
    """Invariant 92(b): [from 300: tap ac] on la starts ac at 300 and lands it at 350, exactly as on a lane with no
    shares; the lane's shares read YIELDED between."""
    tap = Order(AfterTime(300), TapCard(AC))
    r = world(TWO)
    shared = start(r, orders(Order(ALWAYS, SwitchMix(TM)), tap))
    bare = world()
    alone = start(bare, orders(tap))
    for t in (299, 300, 349, 350, 400):
        assert lane_card(advance(shared, r, t), LA) == lane_card(advance(alone, bare, t), LA)
        assert _completions(shared, r, t) == _completions(alone, bare, t)
    assert _completions(shared, r, 349) == 0 and _completions(shared, r, 350) == 1
    assert lane_card(advance(shared, r, 299), LA) is None
    assert lane_card(advance(shared, r, 320), LA) == AC
    assert card_view(shared, r, A1, 320)[0].run == RunKind.YIELDED
    assert lane_card(advance(shared, r, 350), LA) is None


# ---- invariant 93: tap equals share ------------------------------------------------------------------------------

@given(cuts=st.lists(st.integers(0, 400), min_size=1, max_size=6))
def test_a_card_at_bp_in_the_town_mix_equals_the_same_card_run_by_its_always_rule(cuts: list[int]):
    """Invariant 93: for any slicing into advances and views, the store x (continuous line), the card's work and its
    completions are equal at every t; y (a per-completion lump, paid as a rate by the tap and by the share alike)
    is equal at every t too."""
    shared_r = world((joiner("ja", LA, TM, A1),))
    shared = start(shared_r)
    tap_r = world()
    tapped = start(tap_r, orders(always(A1)))
    for t in sorted(set(cuts) | {WORK, 7 * WORK, 400}):
        shared, tapped = advance(shared, shared_r, t), advance(tapped, tap_r, t)
        assert view(shared, shared_r).time == view(tapped, tap_r).time == t
        assert stored(shared, shared_r, X, t) == stored(tapped, tap_r, X, t)
        assert work_done(shared, shared_r, A1, t) == work_done(tapped, tap_r, A1, t)
        assert count(shared, shared_r, A1, t) == count(tapped, tap_r, A1, t)
        assert stored(shared, shared_r, Y, t) == stored(tapped, tap_r, Y, t)


# ---- invariant 57 with town switches, and a greyed town mix --------------------------------------------------------

TAP_LANE = {A1: LA, A2: LA, AC: LA, B1: LB, B2: LB, C1: LC}
ORDER_POOL = st.one_of(
    st.builds(Order, st.sampled_from([ALWAYS, AfterTime(20), AfterTime(60)]),
              st.sampled_from([TapCard(c) for c in TAP_LANE] + [SwitchMix(TM), SwitchMix(TM2)])))


def _breaks_57(s: Save, r: Rules) -> str | None:
    """A latched tap order whose card is unfinished and whose lane holds no tap, at s (the cap carve-out aside)."""
    if s.last_cascade is not None and s.last_cascade.time == s.time:
        return None
    v = view(s, r)
    live = {cv.card for cv in v.cards}
    for o, on in zip(s.orders, s.latches):
        if on and isinstance(o.then, TapCard) and o.then.card in live and lane_card(s, TAP_LANE[o.then.card]) is None:
            return f"{o.then.card} can act at {s.time}"
    return None


def test_the_57_check_can_fail():
    """Control: a latched tap order beside a free lane (set up by hand, which no play reaches) is reported."""
    r = world()
    s = replace(start(r), orders=(always(C1),), latches=(True,))
    assert _breaks_57(s, r) is not None


@given(os=st.lists(ORDER_POOL, max_size=5), cuts=st.lists(st.integers(0, 200), min_size=1, max_size=5))
def test_invariant_57_holds_with_town_switches_among_the_orders(os: list[Order], cuts: list[int]):
    """Invariant 92(b): no latched tap order's card can act (lane free, card unfinished) at any instant, whatever
    town switches stand among the orders and whichever town mix runs; a tap on a joined lane is acted on at once."""
    r = world(TWO + (joiner("jc", LC, TM, None),))
    s = decide(start(r), r, 0, orders(*os))
    for t in sorted(set(cuts) | {0, 20, 60}):
        for dt in (-1, 0, 1):
            if t + dt >= 0:
                s2 = advance(s, r, t + dt)
                assert _breaks_57(s2, r) is None
        s = advance(s, r, t)


def test_a_greyed_town_mix_is_passed_over_and_listed():
    """"Uncapped only" and "Running town mix": retiring a1 greys town:main; the next latched town order's mix runs
    from that instant, and view.greyed_mixes names town:main."""
    retire = TriggerDef(TriggerId("ret"), AfterTime(100), Outcome(unlocks=(Unlock(UnlockKind.RETIRED, A1),)))
    r = world(TWO + (retire,), opening=())
    s = start(r, orders(Order(ALWAYS, SwitchMix(TM)), Order(ALWAYS, SwitchMix(TM2))))
    before, after = view(advance(s, r, 50), r), view(advance(s, r, 150), r)
    assert (before.running_town_mix, before.town_mix_order, TM in before.greyed_mixes) == (TM, 0, False)
    assert (after.running_town_mix, after.town_mix_order, TM in after.greyed_mixes) == (TM2, 1, True)
    assert abs(stored(s, r, X, 150) - 100 * Q) <= 150 and abs(stored(s, r, V, 150) - 50 * Q) <= 150
    alone = start(r, orders(Order(ALWAYS, SwitchMix(TM))))
    assert view(advance(alone, r, 150), r).running_town_mix is None
