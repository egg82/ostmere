"""Drains, part two: forgiveness is the drain's alone, and what it does to the store's other lines (engine DESIGN.txt,
"DRAINS", invariants 125-127). Written blind from that part and the public interface; the `kills` marker names the rows
of MUTANTS_drains.txt each test must turn red for."""
from typing import Any

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, Amount, CardDef, Flow, Pause, StandingDef, advance, new_save, per_hour, segment,
)
from drains_world import CURE, D, I, PER_SECOND, X, at, card_view, cure, kills, mixed, tapped, world

HEAL = ActionId("heal")
HEAL_COST = per_hour(3)
"""A standing action costing 3 items of x an hour: its pause resumes at one hour of that, 3 items."""
SAMPLES = (0, 10, 39, 40, 41, 100, 250, 1000)


def heal() -> StandingDef:
    return StandingDef(HEAL, costs=(Flow(X, HEAL_COST),))


def trickle(items_per_hour: int) -> StandingDef:
    return StandingDef(ActionId(f"in{items_per_hour}"), makes=(Flow(X, per_hour(items_per_hour)),))


# ---- 125: forgiveness is the drain's alone -------------------------------------------------------------------

def _supplied(variant: str, drains: bool) -> CardDef:
    """CURE with an input (10 items of i) or a cost line (1 item a second of i), with or without its drain of x."""
    lines: dict[str, Any] = (
        {"inputs": (Amount(I, 10 * Q),)} if variant == "input" else {"costs": (Flow(I, PER_SECOND),)})
    return cure(**lines) if drains else CardDef(CURE, 100, **lines)


@kills(8)
@pytest.mark.parametrize("variant", ["input", "cost"])
@pytest.mark.parametrize("i0,x0,share_bp", [(4 * Q, 100 * Q, BP), (4 * Q, 0, BP), (25 * Q, 3 * Q, 5_000),
                                           (4 * Q, 2 * Q, 5_000), (200 * Q, 100 * Q, BP)])
def test_inputs_costs_and_their_pauses_are_those_of_the_card_without_its_drains(
        variant: str, i0: int, x0: int, share_bp: int):
    """Invariant 125: at every t the supplies store, the pauses, the card's work and its completions equal the same
    card's without the drain; an input store running dry pauses the card, and with it its drain."""
    with_drain = world(_supplied(variant, True), i0=i0, x0=x0)
    without = world(_supplied(variant, False), i0=i0, x0=x0)
    a, b = mixed(with_drain, share_bp), mixed(without, share_bp)
    saw_pause = False
    for t in SAMPLES + (4, 5, 400):
        sa, sb = advance(a, with_drain, t), advance(b, without, t)
        assert (sa.pauses, sa.cards, at(a, with_drain, I, t)) == (sb.pauses, sb.cards, at(b, without, I, t)), t
        assert card_view(sa, with_drain).completions == card_view(sb, without).completions, t
        saw_pause = saw_pause or bool(sa.pauses)
    assert saw_pause == (variant == "cost" or i0 < 100 * Q), "the control: supplies run out where they should"


@kills(8)
def test_a_card_paused_on_its_input_stops_taking_from_its_drain_store():
    """Invariant 125: 4 items of input pay 40 s of a 100 s completion; the card is then paused on i and x stops falling."""
    r = world(cure(inputs=(Amount(I, 10 * Q),)), i0=4 * Q, x0=100 * Q)
    s = mixed(r)
    assert at(s, r, X, 40) == 96 * Q and at(s, r, X, 1000) == 96 * Q
    a = advance(s, r, 1000)
    assert [(p.runner, p.store) for p in a.pauses] == [(CURE, I)]
    cv = card_view(a, r)
    assert cv.completions == 0 and cv.bar.start_value == 40 * BP


@kills(8)
def test_no_completion_lands_with_an_input_unpaid():
    """Invariant 125: a tap needing 10 items of i with exactly that in store lands with i at 0 and x drained by its
    amount; the same tap short of its input is not ready (its blocker is the input)."""
    r = world(cure(inputs=(Amount(I, 10 * Q),)), i0=10 * Q, x0=30 * Q)
    s = advance(tapped(r), r, 100)
    assert (at(s, r, I, 100), at(s, r, X, 100), card_view(s, r).completions, s.lanes[0].card) == (0, 20 * Q, 1, None)
    short = world(cure(inputs=(Amount(I, 10 * Q),)), i0=10 * Q - 1, x0=30 * Q)
    assert tapped(short).lanes[0].card is None


# ---- 126: other consumers pause ------------------------------------------------------------------------------

@kills(9)
def test_a_standing_cost_on_the_drain_store_is_paused_while_a_drain_runs_at_zero_and_resumes_at_an_hour_of_its_cost():
    """Invariant 126: x reaches 0 at 20 s (2 items fall at 363_000 units a second); the heal is paused from then, as if no
    drain were there; the maker (2 an hour, under the heal's 3) refills x only once the tap has landed at 100, so the
    heal resumes when x holds 3 items, 5400 s later."""
    r = world(cure(), x0=2 * Q, standing=(heal(), trickle(2)))
    s = tapped(r)
    pause = Pause(HEAL, X, 3 * Q)
    assert advance(s, r, 19).pauses == () and at(s, r, X, 19) > 0
    for t in (20, 21, 60, 99, 100, 101):
        assert advance(s, r, t).pauses == (pause,), t
    for t in (20, 60, 99, 100):
        assert at(s, r, X, t) == 0, t
    assert at(s, r, X, 1100) == 1000 * per_hour(2)
    assert advance(s, r, 5499).pauses == (pause,)
    assert advance(s, r, 5500).pauses == () and at(s, r, X, 5500) == 3 * Q


@kills(9)
def test_the_pauses_at_zero_are_those_of_the_same_save_without_the_drain_running():
    r = world(cure(), x0=0, standing=(heal(),))
    drained, untouched = mixed(r), new_save(r)
    for t in (1, 10, 1000):
        a, b = advance(drained, r, t), advance(untouched, r, t)
        assert a.pauses == b.pauses == (Pause(HEAL, X, 3 * Q),), t
        assert at(drained, r, X, t) == at(untouched, r, X, t) == 0


@kills(10)
def test_an_inflow_above_the_consumers_cost_keeps_it_running_while_the_drain_forgives_at_zero():
    """Invariants 126, 127: with 4 an hour coming in and the heal taking 3, n = 1 an hour is above 0 so nothing is
    paused, though the drain (360_000 units a second) takes all of it. Above 0, x falls at n - d (DESIGN.txt, CHOICES
    (drains), "Above 0 the store moves at n - d"), so it is still 20 * n above 0 at 20 s and reads 0 from 21 s to the
    landing, then rises at n."""
    r = world(cure(), x0=2 * Q, standing=(heal(), trickle(4)))
    s = tapped(r)
    n = per_hour(1)
    for t in (1, 19, 20, 21, 50, 99, 100, 101, 300):
        assert advance(s, r, t).pauses == (), t
    assert at(s, r, X, 20) == 2 * Q - 20 * (D - n)
    assert [at(s, r, X, t) for t in (21, 50, 99, 100)] == [0] * 4
    assert at(s, r, X, 200) == 100 * n


# ---- 127: the remainder rises ----------------------------------------------------------------------------------

@kills(11)
@pytest.mark.parametrize("a,work_s,rate", [(Q // 2, 3600, 500), (Q, 3600, 0), (Q, 1800, 0), (Q // 4, 3600, 750)],
                         ids=["n above d", "n equals d", "n below d", "n well above d"])
def test_at_zero_the_store_rises_at_n_minus_d_when_that_is_not_negative_and_stays_otherwise(
        a: int, work_s: int, rate: int):
    """Invariant 127: the maker nets 1000 units a second (4 an hour in, the heal's 3 out) and the mixed cure drains
    a / work_s a second; x starts at 0, with nothing paused."""
    r = world(cure(a, work_s=work_s), x0=0, standing=(heal(), trickle(4)))
    s = mixed(r)
    assert segment(s, r, X).rate == rate and s.pauses == ()
    for t in (1, 60, 3600, 7200):
        assert at(s, r, X, t) == rate * t, t
        assert advance(s, r, t).pauses == (), t
