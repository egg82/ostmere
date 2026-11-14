"""The budget: its formula rounded half up, what musts leave of it (never below 0), which passing non-musts it keeps,
the late addition outside it, and its independence from the day number (statement 12)."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import Fade, Press
from journal_check import budget
from journal_world import (
    PLAIN, beat, blanks, compose_next, compose_span, find_save, note, of, ref_roll, routine, row, shows, slots_of,
    worry,
)

FIVE = tuple(routine(f"r{i}") for i in range(5))
TOLD = (row(0, *(note(r, "first") for r in FIVE)),)
"""Five routines told on day 0, one written day (s = 1)."""
HALVING = replace(PLAIN, lines_start=4, lines_floor=1, lines_halflife=1.0)
"""At s = 1 the budget is 1 + 3 * 0.5 = 2.5, which rounds half up to 3."""


def test_the_budget_rounds_half_up():
    """Statement 12: `round_half_up(2.5)` is 3 (Python's `round` would give 2): three of five passing non-musts kept."""
    day = compose_next(1, TOLD, [shows(r, d) for r in FIVE for d in (0, 1)], FIVE, HALVING)
    assert len(day.notes) == 3 and {n.slot for n in day.notes} == {"repeat"}


def test_the_budget_ignores_the_day_number():
    """Statement 12: blank days are not written, so the budget after one written day is 3 however late the day."""
    for blank_days in range(5):
        rows = (*TOLD, *blanks(1, blank_days))
        today = 1 + blank_days
        day = compose_next(1, rows, [shows(r, d) for r in FIVE for d in (0, today)], FIVE, HALVING)
        assert len(day.notes) == 3, blank_days


def test_settledness_never_below_zero_keeps_the_budget_at_its_start():
    """Statement 12 ("Terms"): `s` is never below 0, so beat notes outnumbering written days leave the budget at
    `lines_start` (3 here), not above it."""
    b1, b2 = beat("b1"), beat("b2")
    rows = (row(0, note(b1, "first"), note(b2, "first"), *(note(r, "first") for r in FIVE)),)
    habits = replace(PLAIN, lines_start=3, lines_floor=1, lines_halflife=1.0, beat_refresh=2.0)
    day = compose_next(1, rows, [shows(r, d) for r in FIVE for d in (0, 1)], (*FIVE, b1, b2), habits)
    assert len(day.notes) == 3


def test_musts_take_the_budget_first_and_never_leave_it_negative():
    """Statement 12: non-musts number at most the budget less the must notes, never below 0: a budget of one and three
    musts keep no non-must (a negative remainder must not count from the end)."""
    beats = tuple(beat(f"b{i}") for i in range(3))
    habits = replace(PLAIN, lines_start=1, lines_floor=1)
    day = compose_next(1, TOLD, [shows(s, d) for s in (*FIVE, *beats) for d in (0, 1)], (*FIVE, *beats), habits)
    assert sorted(n.subject for n in day.notes) == ["b0", "b1", "b2"]


def test_musts_leave_the_rest_of_the_budget_to_non_musts():
    """Statement 12: a budget of three and one must keep two non-musts."""
    b = beat("b")
    day = compose_next(1, TOLD, [shows(s, d) for s in (*FIVE, b) for d in (0, 1)], (*FIVE, b),
                       replace(PLAIN, lines_start=3, lines_floor=3))
    assert slots_of(day, b) == ["first"] and sum(1 for n in day.notes if n.slot == "repeat") == 2


def test_catchup_and_correction_notes_count_against_the_budget():
    """Statement 12: the must notes are own, catch-up and correction alike: with a budget of three, one catch-up and one
    correction leave room for one non-must."""
    caught, wrong = beat("caught"), routine("wrong", misremember=1)
    rows = (row(0, note(wrong, "misremember"), *(note(r, "first") for r in FIVE)), row(1, gap="away"))
    lines = [shows(wrong, 0), shows(caught, 1)] + [shows(r, d) for r in FIVE for d in (0, 2)]
    habits = replace(PLAIN, lines_start=3, lines_floor=3, correct_after_days=2)
    day = compose_next(1, rows, lines, (*FIVE, caught, wrong), habits)
    assert slots_of(day, caught) == ["catchup"] and slots_of(day, wrong) == ["correction"]
    assert sum(1 for n in day.notes if n.slot == "repeat") == 1


def test_a_late_addition_is_outside_the_budget():
    """Statement 12: a late addition takes no room: a budget of two, one must and a late addition keep one non-must."""
    lately, b = routine("lately", late=1), beat("b")
    habits = replace(PLAIN, lines_start=2, lines_floor=2, late_rate=1.0)
    subs = (*FIVE, lately, b)
    lines = [shows(lately, 0), shows(b, 1)] + [shows(r, d) for r in FIVE for d in (0, 1)]
    day = compose_next(1, (row(0, note(lately, "first"), *(note(r, "first") for r in FIVE)),), lines, subs, habits)
    assert slots_of(day, lately) == ["late"] and slots_of(day, b) == ["first"]
    assert sum(1 for n in day.notes if n.slot == "repeat") == 1


def test_the_highest_care_is_kept():
    """Statement 12: the passing non-musts kept are those of highest care (fewest tellings at fade 0.9)."""
    subs = tuple(routine(f"t{w}", repeat=4) for w in range(1, 5))
    rows = tuple(row(d, *(note(s, "first" if d == 0 else "repeat", max(d - 1, 0)) for s in subs[d:])) for d in range(4))
    today = 4
    habits = replace(PLAIN, routine=Fade(1.0, 0.9), lines_start=2, lines_floor=2)
    save_id = find_save(lambda sid: all(ref_roll(sid, today, s.id, "write") < 0.6 for s in subs))
    day = compose_next(save_id, rows, [shows(s, d) for s in subs for d in range(5)], subs, habits)
    assert sorted(n.subject for n in day.notes) == ["t1", "t2"]


@given(save_id=st.integers(0, 2**40))
def test_ties_in_care_keep_the_lower_order_roll(save_id: int):
    """Statement 12: among equal care, the kept are those of lower `roll(..., "order")`; a worry capped at care 1 ties
    with a routine at care 1 (statement 10's cap)."""
    capped = worry("zz", repeat=1)
    subs = (*FIVE, capped)
    habits = replace(PLAIN, worry=Press(1.0, 1.0), lines_start=2, lines_floor=2)
    rows = (row(0, *(note(s, "first") for s in subs)),)
    day = compose_next(save_id, rows, [shows(s, d) for s in subs for d in (0, 1)], subs, habits)
    lowest = sorted(subs, key=lambda s: ref_roll(save_id, 1, s.id, "order"))[:2]
    assert sorted(n.subject for n in day.notes) == sorted(s.id for s in lowest)


def test_the_budget_thins_as_the_journal_settles():
    """Statement 12: with steady activity of always-passing non-musts, each day writes exactly the budget of its
    settledness, which falls as written days accumulate."""
    subs = tuple(routine(f"r{i}", repeat=3) for i in range(8))
    habits = replace(PLAIN, lines_start=6, lines_floor=1, lines_halflife=2.0)
    days = compose_span(1, 12, [shows(s, d) for s in subs for d in range(12)], subs, habits)
    assert len(days[0].notes) == 8
    counts = [len(d.notes) for d in days[1:]]
    assert counts == [budget(days[:d], subs, habits) for d in range(1, 12)]
    assert counts == sorted(counts, reverse=True) and counts[0] > counts[-1] == 1
    assert all(of(days[1], s) == () or slots_of(days[1], s) == ["repeat"] for s in subs)
