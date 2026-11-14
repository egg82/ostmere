"""Properties over generated histories for the shape and must statements: determinism (1), the day and empty gaps (2),
keys from their slots (3), one note per subject a day (4), written once (7), musts on their own day (8) and in the
catch-up after their gap (9). Each composes a whole history a day at a time, as the save writer does."""
import random
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import ComposedDay, Fade, Line
from journal_check import gap_musts, gap_runs, musts_on, own_notes, tellings
from journal_gen import History, histories
from journal_world import compose_span


def _compose(h: History) -> tuple[ComposedDay, ...]:
    return compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)


@given(history=histories(), seed=st.integers(0, 2**32))
def test_the_same_inputs_compose_the_same_whatever_the_line_order(history: History, seed: int):
    """Statement 1 (and `compose_day`'s "any order"): composing twice, the second time with the lines shuffled, gives
    equal rows."""
    shuffled = list(history.lines)
    random.Random(seed).shuffle(shuffled)
    again = compose_span(history.save_id, history.days, shuffled, history.subjects, history.habits)
    assert _compose(history) == again


@given(history=histories())
def test_a_change_counts_wherever_it_sits_in_the_day(history: History):
    """Statement 1 (and `compose_day`'s "any order") where order would bite: each line gets a twin at the same second
    with a key its subject never held, placed after it in one tuple and before it in the other. With fade 0, diligence 1
    and room in the budget, a told routine or crowd is written exactly on a change day, so a change looked for only in
    some of a day's lines (the first, the last) shows as a difference between the two orders."""
    habits = replace(history.habits, routine=Fade(1.0, 0.0), crowd=Fade(1.0, 0.0), floor=1.0, lines_start=50,
                     lines_floor=50, busy_ratio=100.0)
    after: list[Line] = []
    before: list[Line] = []
    for i, line in enumerate(history.lines):
        twin = Line(f"fresh.{i}", line.at, line.source)
        after += [line, twin]
        before += [twin, line]
    assert compose_span(history.save_id, history.days, after, history.subjects, habits) == compose_span(
        history.save_id, history.days, before, history.subjects, habits)


@given(history=histories())
def test_days_and_gaps(history: History):
    """Statement 2: each row is its own day, and a gap row has no notes."""
    for d, r in enumerate(_compose(history)):
        assert r.day == d and (r.gap is None or r.notes == ())


@given(history=histories())
def test_notes_are_drawn_from_their_slots(history: History):
    """Statement 3: every note names a subject in `subjects` and a key of its slot (a mention: of one of its bands)."""
    by_id = {s.id: s for s in history.subjects}
    for r in _compose(history):
        for n in r.notes:
            s = by_id[n.subject]
            slot = tuple(k for b in s.mention for k in b.keys) if n.slot == "mention" else getattr(s, n.slot)
            assert slot and n.key in slot, (r.day, n)


@given(history=histories())
def test_one_note_per_subject_a_day(history: History):
    """Statement 4: per day and subject, one own note at most, and at most one each of catch-up, late and correction."""
    for r in _compose(history):
        for s in history.subjects:
            slots = [n.slot for n in r.notes if n.subject == s.id]
            assert len(own_notes(r, s.id)) <= 1, (r.day, s.id, slots)
            assert all(slots.count(x) <= 1 for x in ("catchup", "late", "correction")), (r.day, s.id, slots)


@given(history=histories())
def test_written_once_without_a_repeat_slot(history: History):
    """Statement 7: a subject with no repeat slot is told by first, repeat, catchup or misremember at most once in the
    whole history."""
    rows = _compose(history)
    for s in history.subjects:
        if not s.repeat:
            told = [n for r in rows for n in r.notes
                    if n.subject == s.id and n.slot in ("first", "repeat", "catchup", "misremember")]
            assert len(told) <= 1, (s.id, told)


@given(history=histories())
def test_every_must_is_written_on_its_own_day(history: History):
    """Statement 8: on a day that is not a gap each must has its own note: `first` (or `misremember`) when untold,
    `repeat` when told, a catch-up that day counting as told."""
    rows = _compose(history)
    by_id = {s.id: s for s in history.subjects}
    for d, r in enumerate(rows):
        if r.gap is not None:
            continue
        for sid in musts_on(rows, d, history.lines, history.subjects):
            told = tellings(rows[:d], sid) + sum(1 for n in r.notes if n.subject == sid and n.slot == "catchup")
            allowed = ["repeat"] if told else ["first", "misremember"] if by_id[sid].misremember else ["first"]
            got = own_notes(r, sid)
            assert len(got) == 1 and got[0] in allowed, (d, sid, got)


@given(history=histories())
def test_every_gap_must_is_caught_up_once_after_its_run(history: History):
    """Statement 9: each must of a gap run has exactly one catch-up note, on the first day after the run (which is then
    written), and no catch-up note appears anywhere else."""
    rows = _compose(history)
    expected: list[tuple[int, str]] = []
    for run in gap_runs(rows):
        after = run[1] + 1
        musts = gap_musts(rows, run, history.lines, history.subjects)
        if after < len(rows) and musts:
            assert rows[after].gap is None and rows[after].notes, (run, musts)
        expected += [(after, sid) for sid in sorted(musts) if after < len(rows)]
    got = sorted((r.day, n.subject) for r in rows for n in r.notes if n.slot == "catchup")
    assert got == sorted(expected)
