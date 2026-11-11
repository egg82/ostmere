"""The worth readout's counting on small fixtures: worth as a fraction (a setup that never lands the set, all of it),
the threshold's sort, a cell, deciles, the longest stretch with no moment, and the opening's span beside each week's."""
from tests.worth import summary as sm

H = 3600


def visit(at: int, moment: bool = False) -> sm.VisitWorth:
    return sm.VisitWorth(1, at, 2, H, 2 * H, 2 * H, H, 2 * H, (), moment, 1.0)


def test_worth_is_the_kept_time_less_the_best_as_a_share_of_the_kept() -> None:
    assert sm.fraction(H, 4 * H) == 0.75
    assert sm.fraction(4 * H, 4 * H) == 0.0
    assert sm.fraction(H, None) == 1.0


def test_the_threshold_sorts_a_visit_on_either_side() -> None:
    kept = 4 * H
    at = kept * (1 - sm.THRESHOLD)
    assert sm.is_moment(at, kept)
    assert not sm.is_moment(at + 60, kept)
    assert sm.is_moment(H, None)


def test_a_cell_marks_a_setup_that_never_lands_and_a_missing_set() -> None:
    assert sm.worth_cell(H, 2 * H) == "+1.0h 50%"
    assert sm.worth_cell(H, None) == "never"
    assert sm.worth_cell(None, None) == "-"


def test_deciles_run_from_the_least_to_the_most() -> None:
    found = sm.deciles([float(x) for x in range(101)])
    assert found[0] == 0 and found[5] == 50 and found[10] == 100
    assert sm.deciles([]) == []


def test_the_longest_dry_stretch_counts_from_the_start_and_to_the_end() -> None:
    visits = [visit(10), visit(20, True), visit(30), visit(80, True)]
    assert sm.longest_dry(visits, 0, 100) == (20, 80)
    assert sm.longest_dry([visit(5, True)], 0, 100) == (5, 100)
    assert sm.longest_dry([], 0, 100) == (0, 100)


def test_the_opening_is_its_own_span_and_each_week_follows() -> None:
    d = sm.DAY_S
    visits = [visit(H, True), visit(2 * H), visit(d + H, True), visit(8 * d + H), visit(9 * d, True)]
    found = sm.spans(visits, 3 * H)
    assert [(s.label, s.visits, s.moments) for s in found] == [("opening", 2, 1), ("week 1", 1, 1), ("week 2", 2, 1)]
    assert found[0].rate == 0.5
