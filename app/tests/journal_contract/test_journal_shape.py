"""The result's shape: its day, a gap's empty notes, notes drawn from their own slots, one note per subject a day
(statements 2-4), and the arguments `compose_day` refuses (its docstring)."""
import pytest

from ashfall_app.saves.journal import DAY_S, ComposedDay, Line, compose_day
from journal_mixed import HABITS, composed, subjects
from journal_world import (
    PLAIN, QUIET, beat, compose_next, compose_span, crowd, note, routine, row, shows, slots_of, worry,
)

B = beat("b", repeat=1)
TRIP = worry("trip", away=2)


def test_the_result_is_the_day_asked_for():
    """Statement 2: the result's `day` is the argument."""
    assert [r.day for r in composed()] == list(range(len(composed())))


def test_a_gap_day_has_no_notes_even_with_a_must_showing():
    """Statement 2 (and 13): a day with `gap` set has no notes, though a beat showed on it."""
    days = compose_span(1, 3, [shows(B, 0), shows(TRIP, 1), shows(B, 1), shows(B, 2)], [B, TRIP], QUIET)
    assert days[1].gap == "away" and days[1].notes == ()
    assert days[2].gap == "away" and days[2].notes == ()


def test_every_note_is_drawn_from_its_own_slot():
    """Statement 3: a note's subject is in `subjects` and its key is in that subject's slot named by its `slot`."""
    by_id = {s.id: s for s in subjects()}
    seen = 0
    for day in composed():
        for n in day.notes:
            s = by_id[n.subject]
            slot = tuple(k for band in s.mention for k in band.keys) if n.slot == "mention" else getattr(s, n.slot)
            assert n.key in slot, n
            seen += 1
    assert seen > 0


def test_a_crowd_mention_is_from_the_band_its_count_reaches():
    """Statement 3 and "Terms": a crowd's later tellings come from the band whose `at_least` is the highest at most that
    day's count of its lines."""
    c = crowd("c", bands=((1, 2), (3, 2), (6, 2)))
    lines = [shows(c, 0, "p0")]
    lines += [shows(c, 1, f"p{i}", second=i) for i in range(5)] + [shows(c, 2, f"p{i}", second=i) for i in range(6)]
    lines += [shows(c, 3, "p0"), shows(c, 4, "p0", second=1), shows(c, 4, "p1", second=2)]
    days = compose_span(5, 5, lines, [c], PLAIN)
    assert slots_of(days[0], c) == ["first"]
    bands = {b.at_least: b.keys for b in c.mention}
    for d, band in ((1, 3), (2, 6), (3, 1), (4, 1)):
        (n,) = days[d].notes
        assert n.slot == "mention" and n.key in bands[band], (d, n)


def test_one_note_per_subject_a_day_besides_catchup_late_and_correction():
    """Statement 4: at most one note of a subject by first, repeat, mention or misremember a day, and its extra notes
    are only a catch-up, a late addition or a correction."""
    for day in composed():
        for s in subjects():
            slots = slots_of(day, s)
            own = [x for x in slots if x in ("first", "repeat", "mention", "misremember")]
            assert len(own) <= 1 and all(slots.count(x) <= 1 for x in ("catchup", "late", "correction")), (day, s.id)


def test_a_line_at_the_days_end_is_refused():
    """`compose_day`'s docstring: a line at or past the day's end raises ValueError."""
    r = routine("r")
    with pytest.raises(ValueError):
        compose_day(1, 0, (Line("r.line", DAY_S, r.source),), (), (r,), PLAIN)
    with pytest.raises(ValueError):
        compose_day(1, 1, (Line("r.line", 5 * DAY_S, r.source),), (row(0),), (r,), PLAIN)


def test_a_line_at_the_days_last_second_is_taken():
    """`compose_day`'s docstring: the day is `[d * 86400, (d + 1) * 86400)`, so its last second is in it."""
    r = routine("r")
    assert slots_of(compose_day(1, 0, (Line("r.line", DAY_S - 1, r.source),), (), (r,), QUIET), r) == ["first"]


@pytest.mark.parametrize("rows", [
    (), (row(0),), (row(0), row(2)), (row(1), row(0)), (row(0), row(1), row(2), row(3)),
], ids=["none", "short", "skips", "out-of-order", "too-many"])
def test_composed_not_exactly_the_days_before_is_refused(rows: tuple[ComposedDay, ...]):
    """`compose_day`'s docstring: `composed` must be exactly days 0 .. day - 1 in order, or ValueError."""
    with pytest.raises(ValueError):
        compose_day(1, 3, (), rows, (B,), PLAIN)


def test_composed_exactly_the_days_before_is_taken():
    """`compose_day`'s docstring, the accepting side of the refusal above."""
    assert compose_next(1, (row(0, note(B, "first")), row(1), row(2)), [], [B], PLAIN) == row(3)


def test_the_mixed_history_writes_and_gaps():
    """Control for the statement 3 and 4 checks above: the history they read has written days and a gap."""
    days = composed()
    assert sum(1 for d in days if d.notes) >= 4 and any(d.gap for d in days) and HABITS.late_rate > 0
