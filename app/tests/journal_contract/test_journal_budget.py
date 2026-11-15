"""The budget: its formula rounded half up, first come (a passing non-must is written while the page holds fewer notes,
musts regardless), the late addition and correction outside it, and its independence from the day number (statement
12)."""
import random
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


def test_a_full_page_takes_no_non_must_and_musts_go_past_it():
    """Statement 12: a budget of one and three musts first keep no non-must; one non-must first, then three musts,
    writes all four."""
    beats = tuple(beat(f"b{i}") for i in range(3))
    habits = replace(PLAIN, lines_start=1, lines_floor=1)
    subs = (*FIVE, *beats)
    musts_first = compose_next(1, TOLD, [shows(s, d) for s in (*beats, *FIVE) for d in (0, 1)], subs, habits)
    assert [n.subject for n in musts_first.notes] == ["b0", "b1", "b2"]
    one_first = compose_next(1, TOLD, [shows(s, d) for s in (FIVE[0], *beats, *FIVE[1:]) for d in (0, 1)], subs, habits)
    assert [n.subject for n in one_first.notes] == ["r0", "b0", "b1", "b2"]


def test_a_must_first_leaves_the_rest_of_the_budget_to_non_musts():
    """Statement 12: a budget of three and one must first keep two non-musts."""
    b = beat("b")
    day = compose_next(1, TOLD, [shows(s, d) for s in (b, *FIVE) for d in (0, 1)], (*FIVE, b),
                       replace(PLAIN, lines_start=3, lines_floor=3))
    assert slots_of(day, b) == ["first"] and sum(1 for n in day.notes if n.slot == "repeat") == 2


def test_catchup_notes_count_against_the_budget_and_a_correction_does_not():
    """Statement 12: with a budget of three, one catch-up leaves room for two non-musts; the correction comes at the
    day's end, outside it."""
    caught, wrong = beat("caught"), routine("wrong", misremember=1)
    rows = (row(0, note(wrong, "misremember"), *(note(r, "first") for r in FIVE)), row(1, gap="away"))
    lines = [shows(wrong, 0), shows(caught, 1)] + [shows(r, d) for r in FIVE for d in (0, 2)]
    habits = replace(PLAIN, lines_start=3, lines_floor=3, correct_after_days=2)
    day = compose_next(1, rows, lines, (*FIVE, caught, wrong), habits)
    assert slots_of(day, caught) == ["catchup"] and slots_of(day, wrong) == ["correction"]
    assert sum(1 for n in day.notes if n.slot == "repeat") == 2


def test_a_late_addition_is_outside_the_budget():
    """Statement 12: a late addition takes no room: a budget of two, one must and a late addition keep one non-must."""
    lately, b = routine("lately", late=1), beat("b")
    habits = replace(PLAIN, lines_start=2, lines_floor=2, late_rate=1.0)
    subs = (*FIVE, lately, b)
    lines = [shows(lately, 0), shows(b, 1)] + [shows(r, d) for r in FIVE for d in (0, 1)]
    day = compose_next(1, (row(0, note(lately, "first"), *(note(r, "first") for r in FIVE)),), lines, subs, habits)
    assert slots_of(day, lately) == ["late"] and slots_of(day, b) == ["first"]
    assert sum(1 for n in day.notes if n.slot == "repeat") == 1


def test_the_earliest_passing_are_kept_whatever_their_care():
    """Statement 12: first come: with room for two, the two passing non-musts whose lines come first are kept, though
    their care (most tellings at fade 0.9) is the lowest."""
    subs = tuple(routine(f"t{w}", repeat=4) for w in range(1, 5))
    rows = tuple(row(d, *(note(s, "first" if d == 0 else "repeat", max(d - 1, 0)) for s in subs[d:])) for d in range(4))
    today = 4
    habits = replace(PLAIN, routine=Fade(1.0, 0.9), lines_start=2, lines_floor=2)
    save_id = find_save(lambda sid: all(ref_roll(sid, today, s.id, "write") < 0.6 for s in subs))
    day = compose_next(save_id, rows, [shows(s, d) for s in reversed(subs) for d in range(5)], subs, habits)
    assert [n.subject for n in day.notes] == ["t4", "t3"]


@given(seed=st.integers(0, 2**32))
def test_the_kept_are_the_first_passing_in_line_order(seed: int):
    """Statement 12: all passing at care 1 and a budget of two, the kept are the first two whose lines come first."""
    capped = worry("zz", repeat=1)
    subs = (*FIVE, capped)
    habits = replace(PLAIN, worry=Press(1.0, 1.0), lines_start=2, lines_floor=2)
    rows = (row(0, *(note(s, "first") for s in subs)),)
    order = list(subs)
    random.Random(seed).shuffle(order)
    day = compose_next(1, rows, [shows(s, 0) for s in subs] + [shows(s, 1) for s in order], subs, habits)
    assert [n.subject for n in day.notes] == [s.id for s in order[:2]]


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
