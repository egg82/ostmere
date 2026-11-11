"""SPENT, when it starts and stops (engine DESIGN.txt, "SPENT", invariants 136, 138 and "The instant"). Written blind
from that part; MUTANTS_spent.txt names the wrong implementations each test must turn red for. EAT at 4000 empties its
pool p at exactly second 100 (spent_world.standard); R1 at 2500 and R2 at 1500 make z and w at their share, so a
share of s moves a store 360 * s units a second."""
from ashfall_app.engine import RunKind, advance, decide, value
from ashfall_app.engine import CardShare, Mix, SaveMix
from spent_world import (
    EAT, EAT2, MIX, P, P2, R1, R2, UNITS_PER_BP as U, W, Y, Z, eater, gains, kills, make_run, mixed, plain, pool_for,
    rate, refill, share_of, spent_kind, standard, world,
)



@kills(12)
def test_a_pool_emptying_changes_the_shares_at_that_instant_and_nowhere_else():
    """Invariant 136: until second 99 every card runs at its saved share; at 100 EAT is SPENT and R1, R2 run at 5000 and
    3000; from there the rates stay constant. z and w follow the piecewise integers exactly."""
    r, s = standard()
    for t in (0, 1, 50, 99):
        assert (make_run(s, r, EAT, t), share_of(s, r, R1, t), rate(s, r, Z, t)) == (RunKind.FULL, 2500, 2500 * U), t
        assert (rate(s, r, W, t), gains(s, r, R1, t)) == (1500 * U, ()), t
    for t in (100, 101, 150, 10_000):
        assert (make_run(s, r, EAT, t), share_of(s, r, R1, t), share_of(s, r, R2, t)) == (spent_kind(), 5000, 3000), t
        assert (rate(s, r, Z, t), rate(s, r, W, t), rate(s, r, P, t), rate(s, r, Y, t)) == (5000 * U, 3000 * U, 0, 0), t
    assert [value(s, r, Z, t) for t in (99, 100, 200)] == [2500 * U * 99, 2500 * U * 100, 2500 * U * 100 + 5000 * U * 100]
    assert [value(s, r, W, t) for t in (100, 200)] == [1500 * U * 100, 1500 * U * 100 + 3000 * U * 100]
    assert [value(s, r, P, t) for t in (99, 100, 500)] == [4000 * U, 0, 0], "p is never negative (invariant 16)"


@kills(12)
def test_the_split_holds_across_the_instant_a_pool_empties():
    """Invariants 1, 136: advance(advance(s, t1), t2) == advance(s, t2) with t1 before, at and after second 100."""
    r, s = standard()
    for t1 in (99, 100, 101):
        for t2 in (101, 100_000):
            assert advance(advance(s, r, t1), r, t2) == advance(s, r, t2), (t1, t2)
    assert share_of(advance(s, r, 100), r, R1, 100) == 5000


@kills(12)
def test_each_pool_that_empties_adds_its_card_and_only_when_it_does():
    """Invariant 136: EAT (1000, p, empty at 100) and EAT2 (2000, p2, empty at 200 once its gain of 400 is
    counted: 2000 for 100 s, then 2400 for 100 s), R1 2000, R2 1000. Until 200 EAT2 is
    still a receiver (R is every other card of the mix whatever its Run, Rsum 5000), so EAT's gain is 400 to R1 and
    200 to R2: R1 is 2000 until 100, 2400 from 100; from 200 K is both and Rsum 3000: R1 3999 (666 and 1333), R2 1999."""
    pool2 = pool_for(2000, 100) + pool_for(2400, 100)
    r = world(eater(), eater(EAT2, P2), *plain(R1, R2), initial={P: pool_for(1000, 100), P2: pool2})
    s = mixed(r, [(EAT, 1000), (EAT2, 2000), (R1, 2000), (R2, 1000)])
    seen = [(share_of(s, r, R1, t), share_of(s, r, R2, t), gains(s, r, R1, t)) for t in (99, 100, 199, 200, 300)]
    assert seen == [(2000, 1000, ()), (2400, 1200, ((EAT, 400),)), (2400, 1200, ((EAT, 400),)),
                    (3999, 1999, ((EAT, 666), (EAT2, 1333))), (3999, 1999, ((EAT, 666), (EAT2, 1333)))]


@kills(4)
def test_a_refill_to_the_resume_level_restores_the_saved_shares_at_its_instant():
    """Invariant 138: 5000 items land at 250 (past any one-hour resume level): at 249 EAT is SPENT, at 250 it runs at its
    saved 4000 and R1, R2 at 2500 and 1500, no pause is left, and p falls again at EAT's share."""
    r, s = standard(triggers=(refill(250, P, 5000),))
    assert (make_run(s, r, EAT, 249), share_of(s, r, R1, 249)) == (spent_kind(), 5000)
    assert (make_run(s, r, EAT, 250), share_of(s, r, R1, 250), share_of(s, r, R2, 250)) == (RunKind.FULL, 2500, 1500)
    assert advance(s, r, 250).pauses == () and gains(s, r, R1, 250) == ()
    assert (rate(s, r, Z, 250), rate(s, r, P, 250)) == (2500 * U, -4000 * U)
    assert value(s, r, P, 300) == 5000 * 3_600_000 - 50 * 4000 * U


@kills(19)
def test_a_refill_below_the_resume_level_leaves_the_card_spent_and_the_yield_in_place():
    """CHOICES, "The share comes back": one item landing at 250 is below the resume level, so EAT stays paused on a store
    that is still spent and R1 keeps 5000."""
    r, s = standard(triggers=(refill(250, P, 1),))
    for t in (249, 250, 251, 400):
        assert (make_run(s, r, EAT, t), share_of(s, r, R1, t)) == (spent_kind(), 5000), t
    assert value(s, r, P, 400) == 3_600_000


@kills(3)
def test_a_refill_of_one_pool_keeps_the_other_spent_cards_gains():
    """Invariant 138, "plus the gains of the cards still spent": p is refilled at 250 while p2 stays empty, so R1 and R2
    hold EAT2's gains alone on top of 2000 and 1000: EAT is a receiver again, so Rsum is 4000 and the gains are 1000
    and 500."""
    r = world(eater(), eater(EAT2, P2), *plain(R1, R2), initial={P: pool_for(1000, 100), P2: pool_for(2000, 200)},
              triggers=(refill(250, P, 5000),))
    s = mixed(r, [(EAT, 1000), (EAT2, 2000), (R1, 2000), (R2, 1000)])
    assert (share_of(s, r, R1, 249), share_of(s, r, R1, 250), share_of(s, r, R2, 250)) == (3999, 3000, 1500)
    assert gains(s, r, R1, 250) == ((EAT2, 1000),)
    assert make_run(s, r, EAT, 250) == RunKind.FULL and make_run(s, r, EAT2, 250) == spent_kind()


@kills(18)
def test_a_player_edit_of_the_running_mix_recomputes_the_yield_at_the_edit():
    """"The instant": a SaveMix at 150 (while p is spent) re-pauses at once and the new saved shares give the new yield:
    EAT 2000, R1 5000, R2 1500 -> R1 5000 + 1538, R2 1500 + 461."""
    r, s = standard()
    s = decide(s, r, 150, SaveMix(Mix(MIX, (CardShare(EAT, 2000), CardShare(R1, 5000), CardShare(R2, 1500)))))
    assert make_run(s, r, EAT, 150) == spent_kind()
    assert (share_of(s, r, R1, 150), share_of(s, r, R2, 150)) == (6538, 1961)
    assert gains(s, r, R1, 150) == ((EAT, 1538),) and rate(s, r, Z, 150) == 6538 * U
