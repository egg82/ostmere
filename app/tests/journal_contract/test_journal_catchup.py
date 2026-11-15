"""Catch-up after a gap: every must of the gap run written once by `catchup` on the first written day after it, the
run's other subjects never, and a catch-up a telling for the rest of its day (statement 9). TRIP, a worry with two
away days, makes the gaps; QUIET habits leave only musts written."""
from dataclasses import replace

from journal_world import (
    PLAIN, QUIET, beat, compose_span, crowd, of, person, routine, shows, slots_of, worry,
)

TRIP = worry("trip", away=2)
"""Showing on day 1, days 1 and 2 are an away gap; day 3 is the first that can be written."""


def test_a_must_in_a_gap_is_caught_up_on_the_first_day_after():
    """Statement 9: a beat showing on a gap day is written once by `catchup` on the first written day after the run,
    even when that day has no lines of its own (it is not blank: a catch-up is owed, statement 15)."""
    b = beat("b")
    days = compose_span(1, 6, [shows(TRIP, 1), shows(b, 1)], [b, TRIP], QUIET)
    assert [d.gap for d in days] == [None, "away", "away", None, None, None]
    assert [(n.subject, n.slot, n.key) for n in days[3].notes] == [("b", "catchup", b.catchup[0])]
    assert all(d.notes == () for d in days[4:])


def test_a_must_showing_on_every_gap_day_is_caught_up_once():
    """Statement 9: written exactly once, however many gap days it showed on."""
    p = person("p")
    days = compose_span(1, 5, [shows(TRIP, 1), shows(p, 1), shows(p, 2, second=5)], [p, TRIP], QUIET)
    assert sum(slots_of(d, p).count("catchup") for d in days) == 1 and slots_of(days[3], p) == ["catchup"]
    assert all(slots_of(d, p) in ([], ["catchup"]) for d in days)


def test_a_catchup_is_a_telling_for_the_rest_of_its_day():
    """Statements 9 and 4: a beat caught up and showing again that day is told, so it is written by `repeat` beside its
    catch-up note, never `first`; with no repeat slot the catch-up note is all."""
    with_repeat, without = beat("br", repeat=1), beat("bn")
    lines = [shows(TRIP, 1)] + [shows(s, d) for s in (with_repeat, without) for d in (1, 3)]
    days = compose_span(1, 4, lines, [with_repeat, without, TRIP], QUIET)
    assert slots_of(days[3], with_repeat) == ["catchup", "repeat"]
    assert slots_of(days[3], without) == ["catchup"]


def test_an_untold_routine_in_a_gap_is_caught_up_and_then_told():
    """Statements 7 and 9: an untold routine is a must on its gap day, so it is caught up; showing again on the catch-up
    day it is told, so with no care it is not written a second time."""
    r = routine("r")
    days = compose_span(1, 4, [shows(TRIP, 1), shows(r, 2), shows(r, 3)], [r, TRIP], QUIET)
    assert slots_of(days[3], r) == ["catchup"]


def test_a_gaps_non_musts_are_never_written_later():
    """Statement 9: the run's other subjects (a told routine, a worry, a crowd) are never written later, however high
    their care; only the must is caught up."""
    r, w, c, b = routine("r"), worry("w"), crowd("c"), beat("b")
    lines = [shows(r, 0), shows(TRIP, 1), shows(b, 1)] + [shows(s, 2) for s in (r, w, c)]
    days = compose_span(1, 5, lines, [r, w, c, b, TRIP], PLAIN)
    assert slots_of(days[0], r) == ["first"]
    assert [n.subject for n in days[3].notes] == ["b"] and all(d.notes == () for d in days[4:])


def test_a_told_subject_with_no_repeat_is_not_caught_up():
    """Statements 7 and 9: a beat told with an empty `repeat` has no slot to tell it by, so it is no must in a gap."""
    b = beat("b")
    days = compose_span(1, 5, [shows(b, 0), shows(TRIP, 1), shows(b, 2)], [b, TRIP], QUIET)
    assert slots_of(days[0], b) == ["first"] and all(d.notes == () for d in days[1:])


def test_the_away_subject_itself_is_caught_up_when_a_must():
    """Statements 9 and 13: the away subject's own day is in its gap, so a beat that sends the writer away is written
    by its catch-up on the day the gap ends."""
    storm = beat("storm", away=3)
    days = compose_span(1, 5, [shows(storm, 1)], [storm], QUIET)
    assert [d.gap for d in days] == [None, "away", "away", "away", None]
    assert slots_of(days[4], storm) == ["catchup"]


def test_a_must_in_a_busy_gap_is_caught_up():
    """Statements 9 and 14: a busy day is a gap too, and its musts are caught up."""
    subs = [beat("b1"), beat("b2"), beat("b3")]
    habits = replace(QUIET, lines_start=1, lines_floor=1, busy_ratio=2.0)
    days = compose_span(1, 2, [shows(s, 0) for s in subs], subs, habits)
    assert days[0].gap == "busy" and days[0].notes == ()
    assert sorted((n.subject, n.slot) for n in days[1].notes) == [(s.id, "catchup") for s in subs]


def test_every_must_is_written_within_its_runs_length_plus_one():
    """Statement 9: a must showing on a gap run's first day is written within the run's length plus one day."""
    b = beat("b", repeat=1)
    long_trip = worry("long", away=4)
    days = compose_span(1, 7, [shows(long_trip, 1), shows(b, 1), shows(b, 6)], [b, long_trip], QUIET)
    assert [d.day for d in days if of(d, b)] == [5, 6]
    assert slots_of(days[5], b) == ["catchup"] and slots_of(days[6], b) == ["repeat"]


def test_a_gap_must_with_no_catchup_slot_is_dropped():
    """Statements 7 and 9: on a gap day a subject is a must only when its `catchup` slot is non-empty; a beat with
    none is dropped with the run's other subjects, so the day after the gap writes only the other beat's catch-up,
    and the dropped beat, still untold, is a first when it shows again."""
    bare, kept = replace(beat("bare"), catchup=()), beat("kept")
    lines = [shows(TRIP, 1), shows(bare, 1), shows(kept, 1), shows(bare, 5)]
    days = compose_span(1, 6, lines, [bare, kept, TRIP], QUIET)
    assert [(n.subject, n.slot) for n in days[3].notes] == [("kept", "catchup")]
    assert [d.day for d in days if of(d, bare)] == [5] and slots_of(days[5], bare) == ["first"]
