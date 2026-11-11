"""SPENT, what a spent store changes beyond the yield (engine DESIGN.txt, "SPENT", invariants 135, 139 and the amended
41). Written blind from that part and api/CONTRACT.txt; MUTANTS_spent.txt names the wrong implementations each test
must turn red for."""
from ashfall_app.engine import ActionId, Flow, RunKind, StandingDef, advance, per_hour, value, view
from spent_world import (
    EAT, P, R1, UNITS_PER_BP as U, Z, card_view, gained_of, kills, make_run, rate, refill,
    scenarios, begin, share_of, spent_kind, spent_store_of, standard,
)


SRC = StandingDef(ActionId("src"), makes=(Flow(P, per_hour(1)),))
"""A standing action refilling p at 1000 units a second: a maker in play, far below what EAT costs."""


@kills(1)
def test_a_paused_card_resumes_when_the_store_reaches_the_resume_level_not_before():
    """Invariant 139: with p made by a standing action, 5000 items landing at 500 (past any one-hour level) lift the pause
    at that instant; one second before, EAT is still PAUSED and R1 still runs its share."""
    r, s = standard(standing=(SRC,), triggers=(refill(500, P, 5000),))
    assert (make_run(s, r, EAT, 499), share_of(s, r, R1, 499)) == (RunKind.PAUSED, 5000)
    assert spent_store_of(card_view(s, r, EAT, 499)) is None
    assert (make_run(s, r, EAT, 500), share_of(s, r, R1, 500)) == (RunKind.FULL, 2500)
    assert value(s, r, P, 500) > 0


@kills(1)
def test_with_no_spent_card_every_view_and_rate_is_what_it_was():
    """Invariant 135: a pool that does not empty in the window leaves every card FULL at its saved share with no gains and
    no spent store, and each store moves at the saved shares."""
    r, s = standard(t_empty=10_000)
    for t in (0, 100, 5000):
        for cv in view(advance(s, r, t), r).cards:
            assert (cv.run, gained_of(cv), spent_store_of(cv)) == (RunKind.FULL, (), None), (t, cv.card)
        assert (share_of(s, r, R1, t), rate(s, r, Z, t)) == (2500, 2500 * U)
    assert make_run(s, r, EAT, 9999) == RunKind.FULL and make_run(s, r, EAT, 10_000) == spent_kind()


@kills(14)
def test_a_line_is_not_starved_by_a_spent_card_alone_but_is_by_a_paused_one_with_a_cure_in_play():
    """Amended invariant 41, LedgerLine.starved: p at 0 with only a spent card on it is not starved (no cure in reach);
    the same with a maker of p in play but not running (an unmixed card) is starved."""
    sc = scenarios()
    for name, starved in (("no maker", False), ("unmixed card maker", True)):
        s, rules = begin(sc[name]), sc[name].rules
        line = next(ln for ln in view(advance(s, rules, 50), rules).ledger if ln.store == P)
        assert (line.starved, line.segment.rate) == (starved, 0), name
        assert (make_run(s, rules, EAT, 50) == spent_kind()) is not starved, name
