"""A day's page fills as the day goes (docs/design/journal.md, "Written as the day goes"): composed with more of its
lines, or ended, a day only gains notes after those it had (statement 22), and each habit that used to compare across
the whole day decides at its moment: busy and away break the day off and keep what came before, the budget is first
come, a crowd is tallied at the day's end, and a note stands where the line that wrote it falls."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import DAY_S, ComposedDay, Fade, Line, Press, compose_day
from journal_gen import History, histories
from journal_world import (
    PLAIN, QUIET, beat, crowd, find_save, lines_before, note, ref_roll, routine, row, shows, worry,
)


def _in_order(lines: tuple[Line, ...]) -> tuple[Line, ...]:
    """The lines as a save stores them: in game-time order (ties as given)."""
    return tuple(sorted(lines, key=lambda ln: ln.at))


def _days(h: History, lines: tuple[Line, ...]) -> list[ComposedDay]:
    rows: list[ComposedDay] = []
    for d in range(h.days):
        rows.append(compose_day(h.save_id, d, lines_before(lines, d), tuple(rows), h.subjects, h.habits))
    return rows


def _begins(more: ComposedDay, fewer: ComposedDay) -> bool:
    return (more.notes[:len(fewer.notes)] == fewer.notes and more.marks[:len(fewer.marks)] == fewer.marks
            and (fewer.gap is None or more.gap == fewer.gap))


@given(history=histories(), cut=st.integers(0, 2**16))
def test_a_day_composed_with_more_of_its_lines_begins_with_the_notes_it_had(history: History, cut: int):
    """Statement 22: for every day, composed open with its lines cut after any one of them, then with one line more, then
    ended, each page begins with the one before it: notes, marks and gap."""
    lines = _in_order(history.lines)
    rows = _days(history, lines)
    d = cut % history.days
    today = [i for i, ln in enumerate(lines) if d * DAY_S <= ln.at < (d + 1) * DAY_S]
    known = lines_before(lines, d - 1) if d else ()
    pages = [compose_day(history.save_id, d, known, tuple(rows[:d]), history.subjects, history.habits, ended=False)]
    for i in today:
        pages.append(compose_day(history.save_id, d, lines[:i + 1], tuple(rows[:d]), history.subjects, history.habits,
                                 ended=False))
    pages.append(rows[d])
    for fewer, more in zip(pages, pages[1:]):
        assert _begins(more, fewer), (d, fewer, more)


def test_an_open_day_writes_nothing_owed_at_its_end():
    """Statement 22: until the day has ended, no crowd, late addition or correction is written; at its end the crowd
    comes first, then the late addition its note made room for."""
    b, c = beat("b", late=1), crowd("c")
    late = replace(PLAIN, late_rate=1.0)
    day0 = compose_day(1, 0, (shows(b, 0),), (), (b, c), late)
    assert day0.notes == (note(b, "first"),)
    lines = (shows(b, 0), shows(c, 1, "c.who.0"))
    assert compose_day(1, 1, lines, (day0,), (b, c), late, ended=False).notes == ()
    assert compose_day(1, 1, lines, (day0,), (b, c), late).notes == (note(c, "first"), note(b, "late"))


def test_a_busy_day_keeps_what_was_written_before_it_got_busy():
    """Busy breaks the day off at the subject that tips it: at ratio 1 and budget 2, the third beat of the day makes the
    rest of it a gap, and the two written before stay; the third is caught up the next day."""
    subs = [beat(f"b{i}") for i in range(3)]
    habits = replace(QUIET, lines_start=2, lines_floor=2, busy_ratio=1.0)
    lines = tuple(shows(s, 0, second=i + 1) for i, s in enumerate(subs))
    day0 = compose_day(1, 0, lines, (), tuple(subs), habits)
    assert day0.gap == "busy" and [n.subject for n in day0.notes] == ["b0", "b1"]
    day1 = compose_day(1, 1, lines, (day0,), tuple(subs), habits)
    assert day1.notes == (note("b2", "catchup"),)


def test_an_away_subject_breaks_the_day_off_at_its_line():
    """Away begins at the subject's moment: a beat written earlier that day stays, and the day is an away gap."""
    b, trip = beat("b"), worry("trip", away=2)
    day0 = compose_day(1, 0, (shows(b, 0, second=1), shows(trip, 0, second=2)), (), (b, trip), QUIET)
    assert day0.gap == "away" and day0.notes == (note(b, "first"),)


def test_the_budget_is_first_come():
    """A non-must that passes is written while the page holds fewer notes than the budget, whatever its care: at budget
    1 the earlier routine (care 0.5) is written and the later worry (care 1) is not."""
    r, w = routine("r", repeat=1), worry("w")
    habits = replace(PLAIN, routine=Fade(1.0, 0.5), worry=Press(1.0, 0.0), lines_start=1, lines_floor=1)
    save_id = find_save(lambda s: ref_roll(s, 1, "r", "write") < 0.5)
    day0 = row(0, note(r, "first"))
    day1 = compose_day(save_id, 1, (shows(r, 0), shows(r, 1, second=1), shows(w, 1, second=2)), (day0,), (r, w),
                       habits)
    assert [n.subject for n in day1.notes] == ["r"]


def test_a_crowd_is_tallied_at_the_days_end_after_the_days_own_notes():
    """A crowd's band needs the day's count, so it is weighed at the day's end and stands after the day's own notes,
    though its first line came first."""
    b, c = beat("b"), crowd("c")
    lines = (shows(c, 0, "c.who.0", second=1), shows(b, 0, second=2), shows(c, 0, "c.who.1", second=3))
    day0 = compose_day(1, 0, lines, (), (b, c), PLAIN)
    assert [n.subject for n in day0.notes] == ["b", "c"]


def test_a_change_later_in_the_day_writes_the_subject_where_the_change_falls():
    """A told routine at care 0 is not written at its first line; a later line with a key it never held is a moment of
    its own at full care, and the note stands there, after a beat that came between."""
    r, b = routine("r", repeat=1), beat("b")
    habits = replace(PLAIN, routine=Fade(1.0, 0.0))
    day0 = compose_day(1, 0, (shows(r, 0),), (), (r, b), habits)
    lines = (shows(r, 0), shows(r, 1, second=1), shows(b, 1, second=2), shows(r, 1, "r.new", second=3))
    day1 = compose_day(1, 1, lines, (day0,), (r, b), habits)
    assert [(n.subject, n.slot) for n in day1.notes] == [("b", "first"), ("r", "repeat")]


def test_lines_in_one_second_stand_in_the_order_stored():
    """Two subjects first shown in the same second are written in the order their lines were stored, not by id."""
    b0, b1 = beat("b0"), beat("b1")
    day0 = compose_day(1, 0, (shows(b1, 0, second=4), shows(b0, 0, second=4)), (), (b0, b1), QUIET)
    assert [n.subject for n in day0.notes] == ["b1", "b0"]
