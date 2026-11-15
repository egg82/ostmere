"""Gaps and blanks: an away subject's days, a busy day by the day's own subjects against the budget, and a blank day
that owes nothing (statements 13-15)."""
from dataclasses import replace

from journal_world import (
    PLAIN, QUIET, beat, compose_next, compose_span, crowd, note, routine, row, shows, slots_of, worry,
)

B = beat("b", repeat=1)


def test_an_away_subject_makes_its_days_a_gap():
    """Statement 13: `away_days = 3` showing on day 1 makes days 1, 2 and 3 an away gap, and day 4 not."""
    trip = worry("trip", away=3)
    days = compose_span(1, 6, [shows(trip, 1)] + [shows(B, d) for d in range(6)], [B, trip], QUIET)
    assert [d.gap for d in days] == [None, "away", "away", "away", None, None]
    assert all(d.notes == () for d in days[1:4]) and days[4].notes and days[5].notes


def test_away_from_day_zero_and_for_one_day():
    """Statement 13: the gap starts on the subject's own day, day 0 included; `away_days = 1` is that day alone."""
    once = worry("once", away=1)
    days = compose_span(1, 3, [shows(once, 0), shows(B, 1)], [B, once], QUIET)
    assert [d.gap for d in days] == ["away", None, None]


def test_overlapping_aways_join():
    """Statement 13: two away subjects whose spans overlap gap every day either covers."""
    a, b = worry("a", away=2), routine("b", away=2)
    days = compose_span(1, 5, [shows(a, 1), shows(b, 2)], [a, b], QUIET)
    assert [d.gap for d in days] == [None, "away", "away", "away", None]


def test_a_day_busier_than_the_budget_allows_is_a_busy_gap():
    """Statement 14: more subjects shown so far than `busy_ratio * budget` (strictly) breaks the day off: at ratio 1.5
    and budget 2, three showing are written and the fourth makes the rest of the day busy, musts and all."""
    subs = [beat(f"b{i}") for i in range(4)]
    habits = replace(QUIET, lines_start=2, lines_floor=2, busy_ratio=1.5)
    three = compose_next(1, (), [shows(s, 0) for s in subs[:3]], subs, habits)
    assert three.gap is None and len(three.notes) == 3
    four = compose_next(1, (), [shows(s, 0) for s in subs], subs, habits)
    assert four.gap == "busy" and [n.subject for n in four.notes] == ["b0", "b1", "b2"]


def test_a_crowd_counts_once_however_many_came():
    """Statement 14: busy counts subjects showing, so a crowd of many lines is one."""
    c = crowd("c")
    habits = replace(QUIET, lines_start=1, lines_floor=1, busy_ratio=2.0)
    day = compose_next(1, (), [shows(c, 0, f"who.{i}", second=i) for i in range(6)] + [shows(B, 0)], [B, c], habits)
    assert day.gap is None and slots_of(day, B) == ["first"]


def test_the_same_day_is_written_early_and_busy_once_settled():
    """Statement 14 with 12: busy is against the day's budget, so four subjects fit the opening budget of four, and once
    two written days bring it to two the third breaks the day off."""
    subs = tuple(routine(f"r{i}") for i in range(4))
    habits = replace(PLAIN, lines_start=4, lines_floor=1, lines_halflife=1.0, busy_ratio=1.0)
    first = compose_next(1, (), [shows(s, 0) for s in subs], subs, habits)
    assert first.gap is None and len(first.notes) == 4
    rows = (row(0, *(note(s, "first") for s in subs)), row(1, *(note(s, "repeat") for s in subs)))
    later = compose_next(1, rows, [shows(s, d) for s in subs for d in range(3)], subs, habits)
    assert later.gap == "busy" and [(n.subject, n.slot) for n in later.notes] == [("r0", "repeat"), ("r1", "repeat")]


def test_what_is_owed_does_not_count_toward_busy():
    """Statement 14: catch-ups owed from a gap are not counted, so two catch-ups and two showing subjects against a
    threshold of two is not busy."""
    b1, b2, r1, r2 = beat("b1"), beat("b2"), routine("r1"), routine("r2")
    trip = worry("trip", away=1)
    habits = replace(QUIET, lines_start=2, lines_floor=2, busy_ratio=1.0)
    lines = [shows(r1, 0), shows(r2, 0), shows(trip, 1), shows(b1, 1), shows(b2, 1), shows(r1, 2), shows(r2, 2)]
    days = compose_span(1, 3, lines, [b1, b2, r1, r2, trip], habits)
    assert days[1].gap == "away" and days[2].gap is None
    assert sorted((n.subject, n.slot) for n in days[2].notes) == [("b1", "catchup"), ("b2", "catchup")]


def test_away_wins_over_busy():
    """Statements 13 and 14: at a moment that would tip the day busy, an away subject makes it an away gap."""
    trip = worry("trip", away=1)
    subs = [beat("b0"), trip]
    habits = replace(QUIET, lines_start=1, lines_floor=1, busy_ratio=1.0)
    assert compose_next(1, (), [shows(s, 0) for s in subs], subs, habits).gap == "away"


def test_a_day_with_nothing_to_write_is_blank():
    """Statement 15: no lines, or only subjects failing their roll, is no notes and no gap."""
    r = routine("r")
    assert compose_next(1, (), [], [r], PLAIN) == row(0)
    assert compose_next(1, (row(0, note(r, "first")),), [shows(r, 0), shows(r, 1)], [r], QUIET) == row(1)


def test_nothing_is_owed_after_a_blank():
    """Statement 15: a non-must that failed its roll on a blank day is not written later, nor a late addition kept
    across the blank."""
    r, lately = routine("r"), routine("lately", late=1)
    habits = replace(QUIET, late_rate=1.0)
    lines = [shows(lately, 0), shows(r, 0), shows(r, 1), shows(B, 2)]
    days = compose_span(1, 3, lines, [r, lately, B], habits)
    assert days[1] == row(1)
    assert [(n.subject, n.slot) for n in days[2].notes] == [("b", "first")]


def test_a_crowd_below_its_bands_still_counts_toward_busy():
    """Statement 14 and "Terms": a told crowd below every band is not written but still shows, so with a budget of one
    at ratio 1 it and a beat make two showing and a busy day."""
    c = crowd("c", bands=((3, 2),))
    habits = replace(PLAIN, lines_start=1, lines_floor=1, busy_ratio=1.0)
    lines = [shows(c, 0, "p0"), shows(c, 1, "p1"), shows(B, 1)]
    day = compose_next(1, (row(0, note(c, "first")),), lines, [c, B], habits)
    assert day.gap == "busy" and day.notes == ()
