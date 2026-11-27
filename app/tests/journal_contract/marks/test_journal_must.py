"""Musts: which subjects must be written, "written once", and musts written on their own day past the budget
(statements 7 and 8). QUIET habits fail every non-must, so whatever is written here is written as a must."""
from dataclasses import replace

from journal_world import (
    PLAIN, QUIET, beat, compose_next, compose_span, crowd, keys, note, of, person, routine, row, shows, slots_of, worry,
)

TIGHT = replace(QUIET, lines_start=1, lines_floor=1, busy_ratio=10.0)
"""A budget of one and room for ten showing subjects before a day is busy."""


def test_beats_and_persons_are_written_first_past_the_budget():
    """Statements 7 and 8: a beat or person showing and not yet told is written by `first` that day, however small the
    budget and however low its care."""
    subs = [beat("b1"), beat("b2"), person("p1"), person("p2")]
    (day,) = compose_span(3, 1, [shows(s, 0) for s in subs], subs, TIGHT)
    assert sorted((n.subject, n.slot, n.key) for n in day.notes) == [
        (s.id, "first", s.first[0]) for s in sorted(subs, key=lambda s: s.id)]
    assert day.gap is None


def test_a_routine_is_a_must_until_told():
    """Statement 7: a routine showing and not yet told is a must (written by `first`); once told it is not, so with no
    care it is not written again."""
    r = routine("r", repeat=2)
    days = compose_span(3, 3, [shows(r, d) for d in range(3)], [r], QUIET)
    assert slots_of(days[0], r) == ["first"] and days[1].notes == () and days[2].notes == ()


def test_a_told_beat_with_a_repeat_slot_is_written_again_by_repeat():
    """Statements 7 and 8: a told beat or person with a repeat slot has a slot to tell it by, so it is a must again,
    written by `repeat`."""
    b, p = beat("b", repeat=2), person("p", repeat=1)
    days = compose_span(3, 3, [shows(s, d) for s in (b, p) for d in range(3)], [b, p], TIGHT)
    assert slots_of(days[0], b) == ["first"] and slots_of(days[0], p) == ["first"]
    for d in (1, 2):
        assert slots_of(days[d], b) == ["repeat"] and of(days[d], b)[0].key in b.repeat
        assert slots_of(days[d], p) == ["repeat"] and of(days[d], p)[0].key in p.repeat


def test_a_told_beat_with_no_repeat_slot_is_written_once():
    """Statement 7: a subject told with an empty `repeat` is never written again, must or not."""
    b, p = beat("b"), person("p")
    days = compose_span(3, 4, [shows(s, d) for s in (b, p) for d in range(4)], [b, p], PLAIN)
    assert slots_of(days[0], b) == ["first"] and slots_of(days[0], p) == ["first"]
    assert all(d.notes == () for d in days[1:])


def test_a_routine_or_worry_with_no_repeat_slot_is_written_once_whatever_its_care():
    """Statement 7, "written once": care 1 and diligence 1 pass every roll, yet a told subject with no `repeat` is not
    written again by any of first, repeat, catchup or misremember."""
    r, w = routine("r", repeat=0), worry("w", repeat=0)
    days = compose_span(3, 5, [shows(s, d, f"{s.id}.{d}") for s in (r, w) for d in range(5)], [r, w], PLAIN)
    assert slots_of(days[0], r) == ["first"] and slots_of(days[0], w) == ["first"]
    assert all(d.notes == () for d in days[1:])


def test_written_once_leaves_a_crowds_mentions():
    """Statement 7 names first, repeat, catchup and misremember, not mention: a crowd (no repeat slot) told by `first`
    goes on by `mention` ("Terms": mention stands in for its repeat)."""
    c = crowd("c", bands=((1, 3),))
    days = compose_span(3, 3, [shows(c, d, f"who.{d}") for d in range(3)], [c], PLAIN)
    assert slots_of(days[0], c) == ["first"] and slots_of(days[1], c) == ["mention"] == slots_of(days[2], c)


def test_a_worry_or_crowd_is_never_a_must():
    """Statement 7: only beats, persons and untold routines are musts; a worry or crowd with no care is not written."""
    w, c = worry("w"), crowd("c")
    days = compose_span(3, 2, [shows(w, d) for d in range(2)] + [shows(c, d) for d in range(2)], [w, c], QUIET)
    assert days[0].notes == () == days[1].notes and days[0].gap is None


def test_told_in_composed_counts_however_it_was_told():
    """Statements 7 and 8: "told" counts every telling in `composed`; a routine told by `repeat` (as stored) is not a
    first again, and a beat told by its catch-up goes on by `repeat`."""
    r, b = routine("r"), beat("b", repeat=1)
    rows = (row(0, note(r, "repeat"), note(b, "catchup")),)
    day = compose_next(3, rows, [shows(r, 1), shows(b, 1)], [r, b], QUIET)
    assert slots_of(day, r) == [] and slots_of(day, b) == ["repeat"]


def test_musts_ignore_the_budget_at_any_settledness():
    """Statement 8: musts are not limited by the budget, here one with a long written history behind it."""
    subs = [beat(f"b{i}") for i in range(6)]
    filler = routine("filler")
    rows = tuple(row(d, note(filler, "first" if d == 0 else "repeat")) for d in range(20))
    day = compose_next(3, rows, [shows(s, 20) for s in subs], [*subs, filler], replace(TIGHT, busy_ratio=50.0))
    assert sorted(n.subject for n in day.notes) == [s.id for s in subs]
    assert {n.key for n in day.notes} == {k for s in subs for k in keys(s.id, "first", 1)}
