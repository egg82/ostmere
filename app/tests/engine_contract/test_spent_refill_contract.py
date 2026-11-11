"""SPENT for a store a maker refills (engine DESIGN.txt, "SPENT", "Giver", "The instant, and the hour", invariants 134,
136, 138 and 139): a paused card's share yields by the one rule whatever can refill its store, from the pause to its
resume. EAT at 4000 costs p at 4000 * 360 units a second, so its resume level is an hour of that, 5_184_000_000 units
(1440 items); R1 at 2500 and R2 at 1500 make z and w at their share. MUTANTS_spent.txt names the wrong implementations
each test must turn red for."""
import pytest

from ashfall_app.engine import ActionId, Flow, RunKind, StandingDef, Unlock, UnlockKind, advance, per_hour, value
from spent_world import (
    EAT, EAT2, P, R1, R2, UNITS_PER_BP as U, W, Z, card_view, eater, gained_of, gains, kills, make_run, maker, mixed,
    opening_without, plain, pool_for, rate, refill, share_of, spent_kind, spent_store_of, standard, unlocking, world,
)

RESUME = 4000 * U * 3600
"""EAT's resume level: one hour of its cost at its saved share."""
SLOW = StandingDef(ActionId("src"), makes=(Flow(P, per_hour(1)),))
"""A standing action refilling p at 1000 units a second: a maker in play, far below what EAT costs."""
HALF = StandingDef(ActionId("src"), makes=(Flow(P, per_hour(720)),))
"""A standing action refilling p at 720_000 units a second, half of what EAT costs: p empties at 200, when it falls at
720_000 a second from pool_for(4000, 100), and climbs back to the resume level 7200 s later."""


@kills(1)
def test_a_card_paused_on_a_store_a_maker_refills_gives_its_share_to_the_rest():
    """Invariants 134, 139: p empties at about 100 under a running mix while a standing action makes it: EAT is PAUSED
    (not SPENT, no spent_store), and R1 and R2 run 5000 and 3000, each naming EAT as the source, as for a spent card."""
    r, s = standard(standing=(SLOW,))
    for t in (110, 111, 500):
        cv = card_view(s, r, EAT, t)
        assert (make_run(s, r, EAT, t), cv.run, spent_store_of(cv)) == (RunKind.PAUSED, RunKind.PAUSED, None), t
        assert (share_of(s, r, R1, t), share_of(s, r, R2, t)) == (5000, 3000), t
        assert (gains(s, r, R1, t), gained_of(card_view(s, r, R2, t))) == (((EAT, 2500),), ((EAT, 1500),)), t
        assert (rate(s, r, Z, t), rate(s, r, W, t), cv.share_bp) == (5000 * U, 3000 * U, 4000), t


@kills(1)
def test_the_share_stays_given_while_the_store_refills_below_the_hour_and_comes_back_at_the_resume():
    """"The instant, and the hour", invariant 139: ten items land at 300, so p is above 0 but below the resume level, and
    the share stays with R1 and R2 at that instant and after; 5000 items at 600 lift the Pause, and from that instant
    EAT runs its saved 4000 and R1, R2 their own 2500 and 1500."""
    r, s = standard(standing=(SLOW,), triggers=(refill(300, P, 10, "some"), refill(600, P, 5000)))
    for t in (299, 300, 301, 599):
        assert (make_run(s, r, EAT, t), share_of(s, r, R1, t), share_of(s, r, R2, t)) == (RunKind.PAUSED, 5000, 3000), t
    assert 0 < value(s, r, P, 300) < RESUME
    assert (make_run(s, r, EAT, 600), share_of(s, r, R1, 600), share_of(s, r, R2, 600)) == (RunKind.FULL, 2500, 1500)
    assert (gains(s, r, R1, 600), advance(s, r, 600).pauses) == ((), ())


@kills(1)
def test_a_maker_refilling_the_store_to_the_hour_brings_the_share_back_then_and_not_before():
    """Invariants 136, 139: p empties at 200 and the standing action brings it to the resume level 7200 s later, at
    7400: the receivers hold the gain on both sides of the store's rise off 0 and give it back exactly then."""
    r, s = standard(standing=(HALF,))
    assert (make_run(s, r, EAT, 199), share_of(s, r, R1, 199)) == (RunKind.FULL, 2500)
    for t in (200, 201, 3800, 7399):
        assert (make_run(s, r, EAT, t), share_of(s, r, R1, t), share_of(s, r, R2, t)) == (RunKind.PAUSED, 5000, 3000), t
    assert value(s, r, P, 7399) < RESUME <= value(s, r, P, 7400)
    assert (make_run(s, r, EAT, 7400), share_of(s, r, R1, 7400), share_of(s, r, R2, 7400)) == (RunKind.FULL, 2500, 1500)


@kills(4)
@pytest.mark.parametrize("kind", ["standing", "card"])
def test_a_maker_coming_into_play_makes_the_card_paused_and_the_receivers_keep_its_share(kind: str):
    """Invariant 138: at 250 an unlock puts a maker of p in play: from 250 EAT is PAUSED (not SPENT), and since it still
    holds its Pause R1 and R2 keep its share until it resumes."""
    cards, standing = (eater(), *plain(R1, R2)), ()
    if kind == "standing":
        standing, locked, unlock = (SLOW,), "src", Unlock(UnlockKind.ACTION, "src")
    else:
        cards, locked, unlock = cards + (maker(EAT2, P),), "eat2", Unlock(UnlockKind.CARD, "eat2")
    r = world(*cards, standing=standing, initial={P: pool_for(4000, 100)}, triggers=(unlocking(250, unlock),),
              opening=opening_without(cards, standing, locked))
    s = mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)])
    assert (make_run(s, r, EAT, 249), share_of(s, r, R1, 249)) == (spent_kind(), 5000)
    for t in (250, 251, 1000):
        assert (make_run(s, r, EAT, t), share_of(s, r, R1, t), share_of(s, r, R2, t)) == (RunKind.PAUSED, 5000, 3000), t
        assert gains(s, r, R1, t) == ((EAT, 2500),) and rate(s, r, Z, t) == 5000 * U, t
