"""SPENT, the yield (engine DESIGN.txt, "SPENT", invariants 134, 137, 141). Written blind from that part and
api/CONTRACT.txt; MUTANTS_spent.txt names the wrong implementations each test must turn red for (the `kills` marker).
Every expectation is hand-worked from "The yield": on a lane, each receiver r gains floor(s_k * s_r / Rsum) from each
spent card k, over the SAVED shares of the lane's other cards. Pools start at 0 here, so EAT is spent from the first
instant and the arithmetic is read at one steady state."""
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AtLeast, CardId, Flow, FlowKind, Modifier, ModifierKind, RateRef, RunKind, SourceId, StandingDef, StoreValue, advance, explain,
    modified_rate, new_save, per_hour,
)
from spent_world import (
    EAT, EAT2, P, P2, R1, R2, UNITS_PER_BP, W, Y, Z, card_view, eater, gained_of, gains, kills, make_run, mixed,
    plain, rate, share_of, spent_kind, spent_store_of, standard, work_of, world,
)


CASES = [
    pytest.param((4000, 2500, 1500), {R1: (5000, 2500), R2: (3000, 1500)}, id="exact"),
    pytest.param((1000, 3333, 3334), {R1: (3832, 499), R2: (3834, 500)}, id="floors, never rounds up"),
    pytest.param((7, 1, 2), {R1: (3, 2), R2: (6, 4)}, id="tiny spent share"),
    pytest.param((100, 1, 1), {R1: (51, 50), R2: (51, 50)}, id="even split"),
]
"""(shares of EAT, R1, R2) -> each receiver's (effective share, the one gain from EAT)."""


@kills(17)
@pytest.mark.parametrize("shares,expected", CASES)
def test_a_receiver_gains_a_floor_of_the_spent_share_in_proportion_to_the_saved_shares(
        shares: tuple[int, ...], expected: dict[CardId, tuple[int, int]]):
    """Invariant 134, one spent card: each receiver's effective share is its saved share plus floor(s_k * s_r / Rsum),
    its `gained` names the spent card with exactly that whole number, and its store moves at the effective share."""
    r, s = standard(shares, t_empty=None)
    for card, (eff, gain) in expected.items():
        assert share_of(s, r, card, 60) == eff, card
        assert gains(s, r, card, 60) == ((EAT, gain),), card
    assert rate(s, r, Z, 60) == expected[R1][0] * UNITS_PER_BP
    assert rate(s, r, W, 60) == expected[R2][0] * UNITS_PER_BP


@kills(1, 13)
def test_the_spent_card_runs_nothing_and_keeps_the_share_the_player_set():
    """Invariant 134 and "Read model": the spent card's lines explain with Run SPENT (0 of 1), per_hour 0, its saved
    share and no gains; CardView.share_bp is the saved share and its run is SPENT on its pool."""
    r, s = standard(t_empty=None)
    for e in (explain(advance(s, r, 60), r, RateRef(EAT, FlowKind.COST, P)),
              explain(advance(s, r, 60), r, RateRef(EAT, FlowKind.MAKE, Y)), work_of(s, r, EAT, 60)):
        assert (e.run.kind, e.run.num, e.run.den, e.per_hour, e.share_bp, gained_of(e)) == (spent_kind(), 0, 1, 0, 4000, ())
    assert explain(advance(s, r, 60), r, RateRef(EAT, FlowKind.COST, P)).run.store == P
    cv = card_view(s, r, EAT, 60)
    assert (cv.run, cv.share_bp, spent_store_of(cv), gained_of(cv), cv.by) == (spent_kind(), 4000, P, (), None)
    assert make_run(s, r, EAT, 60) == spent_kind()


@kills(13, 17)
def test_the_view_gives_a_receiver_its_saved_share_and_its_gains_apart():
    """"Read model" and the wire: CardView.share_bp stays what the player saved, `gained` lists each spent card's part,
    and the receiver is not itself spent (spent_store None)."""
    r, s = standard(t_empty=None)
    cv = card_view(s, r, R1, 60)
    assert (cv.share_bp, gained_of(cv), spent_store_of(cv), cv.run) == (2500, ((EAT, 2500),), None, RunKind.FULL)


@kills(6, 9)
def test_two_spent_cards_each_give_one_rounded_down_part_in_mix_order():
    """Invariants 134, 137: EAT 1000 and EAT2 2000 both spent, R1 2000 and R2 1000 (Rsum 3000). R1 gains 666 and 1333,
    R2 gains 333 and 666: one floor per pair (spent card, receiver), listed in the spent cards' mix order, and a line's
    gains sum to its effective share less its saved one."""
    r = world(eater(), eater(EAT2, P2), *plain(R1, R2))
    s = mixed(r, [(EAT, 1000), (EAT2, 2000), (R1, 2000), (R2, 1000)])
    assert gains(s, r, R1, 5) == ((EAT, 666), (EAT2, 1333))
    assert gains(s, r, R2, 5) == ((EAT, 333), (EAT2, 666))
    assert (share_of(s, r, R1, 5), share_of(s, r, R2, 5)) == (3999, 1999)
    assert rate(s, r, Z, 5) == 3999 * UNITS_PER_BP


@kills(8)
def test_the_proportion_is_over_saved_shares_so_a_waiting_receiver_still_takes_its_part():
    """Invariant 134 ("whatever their Run"): R2 waits on a requires that never holds, yet it stays in R, so R1 gains
    floor(4000 * 2500 / 4000) = 2500, not all 4000; R2 holds its gain of 1500 unused."""
    wait = replace(plain(R2)[0], requires=(AtLeast(StoreValue(P2), Q, Q),))
    r = world(eater(), plain(R1)[0], wait)
    s = mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)])
    assert gains(s, r, R1, 60) == ((EAT, 2500),) and share_of(s, r, R1, 60) == 5000
    assert gains(s, r, R2, 60) == ((EAT, 1500),) and share_of(s, r, R2, 60) == 3000
    assert make_run(s, r, R2, 60) == RunKind.WAITING and rate(s, r, W, 60) == 0


@kills(8)
def test_a_paused_card_gives_its_share_beside_a_spent_one_and_takes_none():
    """CHOICES "Giver": R2 is paused on a store a standing action refills (not spent), so it gives like EAT and is
    out of R: R1 alone receives, 2500 + 4000 + 1500, each source named in the givers' mix order."""
    wait = replace(plain(R2)[0], costs=(Flow(P2, per_hour(3600)),))
    src = StandingDef(ActionId("src"), makes=(Flow(P2, per_hour(1)),))
    r = world(eater(), plain(R1)[0], wait, standing=(src,))
    s = mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)])
    assert gains(s, r, R1, 60) == ((EAT, 4000), (R2, 1500)) and share_of(s, r, R1, 60) == 8000
    assert (make_run(s, r, R2, 60), gains(s, r, R2, 60), rate(s, r, W, 60)) == (RunKind.PAUSED, (), 0)


@kills(20)
@pytest.mark.parametrize("shares", [(4000,), (4000, 0), (4000, 0, 0)])
def test_when_the_rest_of_the_lane_has_no_share_nothing_moves(shares: tuple[int, ...]):
    """Invariant 134: Rsum 0 (EAT alone, or the others at share 0) moves nothing: no gains, saved shares everywhere."""
    r, s = standard(shares, t_empty=None)
    assert make_run(s, r, EAT, 60) == spent_kind()
    for card, saved in zip((R1, R2), shares[1:]):
        assert (share_of(s, r, card, 60), gains(s, r, card, 60)) == (saved, ())
    assert rate(s, r, Z, 60) == 0


@kills(6, 9)
@given(spent=st.integers(1, 9998), first=st.integers(1, 9997))
def test_the_two_oclock_property_the_receivers_take_up_all_but_the_rounding(spent: int, first: int):
    """Invariants 134, 141: with the mix's shares summing to BP, one spent card and two running receivers, the receivers'
    effective shares sum to more than BP - 2 (and at most BP), each is its saved share plus its floored gain."""
    left = BP - spent
    r1 = 1 + (first - 1) % (left - 1)
    r2 = left - r1
    r, s = standard((spent, r1, r2), t_empty=None)
    assert make_run(s, r, R1, 7) == make_run(s, r, R2, 7) != spent_kind()
    total = share_of(s, r, R1, 7) + share_of(s, r, R2, 7)
    assert BP - 2 < total <= BP, (spent, r1, r2, total)
    for card, share in ((R1, r1), (R2, r2)):  # `gained` lists the non-zero terms only (134)
        assert gains(s, r, card, 7) == (((EAT, spent * share // left),) if spent * share // left else ()), card


@kills(17)
def test_explain_names_the_source_and_invariant_ten_holds_on_its_own_fields():
    """Invariants 137, 10: a receiver's lines explain share_bp = saved + the sum of `gained` (each entry a spent card of
    the same mix), and per_hour is the formula on those fields, also under a modifier aimed at the line."""
    mod = Modifier(RateRef(R1, FlowKind.MAKE, Z), ModifierKind.MUL_BP, 20_000, SourceId("m"))
    r, _ = standard(t_empty=None)
    s = mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)], base=new_save(r, (mod,)))
    ref = RateRef(R1, FlowKind.MAKE, Z)
    for e in (explain(advance(s, r, 9), r, ref), work_of(s, r, R1, 9)):
        assert e.share_bp == 2500 + sum(g for _, g in gained_of(e)) == 5000
        assert {c for c, _ in gained_of(e)} == {EAT}
    e = explain(advance(s, r, 9), r, ref)
    assert isinstance(e.ref, RateRef)
    assert e.per_hour == modified_rate(e.ref, e.base_per_hour, e.share_bp, e.adds + e.muls, e.run).per_hour
    assert e.per_hour == 2 * 5000 * UNITS_PER_BP
