"""The contract's own definitions (journal.py's module docstring, "Terms"), read off a composed history so the
properties can state their invariants: what shows on a day, a subject's tellings, settledness, the budget, which
subjects are musts, and the gap runs. Each is a definition, never a decision the composer makes by roll."""
import math
from collections.abc import Sequence

from ashfall_app.saves.journal import DAY_S, ComposedDay, Habits, Line, Subject
from journal_world import OWN_SLOTS, TELLING_SLOTS


def showing(lines: Sequence[Line], subjects: Sequence[Subject], day: int) -> list[Subject]:
    """The subjects a line shows on `day`, in `subjects`' order."""
    sources = {line.source for line in lines if day * DAY_S <= line.at < (day + 1) * DAY_S}
    return [s for s in subjects if s.source in sources]


def tellings(rows: Sequence[ComposedDay], subject_id: str) -> int:
    return sum(1 for r in rows for n in r.notes if n.subject == subject_id and n.slot in TELLING_SLOTS)


def settledness(rows: Sequence[ComposedDay], subjects: Sequence[Subject], habits: Habits) -> float:
    beats = {s.id for s in subjects if s.kind == "beat"}
    written = sum(1 for r in rows if r.notes)
    beat_notes = sum(1 for r in rows for n in r.notes if n.subject in beats)
    return max(0.0, written - habits.beat_refresh * beat_notes)


def budget(rows: Sequence[ComposedDay], subjects: Sequence[Subject], habits: Habits) -> int:
    s = settledness(rows, subjects, habits)
    raw = habits.lines_floor + (habits.lines_start - habits.lines_floor) * 0.5 ** (s / habits.lines_halflife)
    return math.floor(raw + 0.5)


def is_must(subject: Subject, told: int) -> bool:
    """Statement 7, for a subject that shows: a beat or person with a slot to tell it by, or a routine not yet told."""
    if subject.kind in ("beat", "person"):
        return bool(subject.first) if told == 0 else bool(subject.repeat)
    return subject.kind == "routine" and told == 0


def musts_on(rows: Sequence[ComposedDay], day: int, lines: Sequence[Line], subjects: Sequence[Subject]) -> set[str]:
    """The musts among `day`'s own subjects, counting a catch-up note on that day as a telling (statement 9)."""
    before, today = rows[:day], rows[day]
    caught = {n.subject for n in today.notes if n.slot == "catchup"}
    return {s.id for s in showing(lines, subjects, day) if is_must(s, tellings(before, s.id) + (s.id in caught))}


def gap_runs(rows: Sequence[ComposedDay]) -> list[tuple[int, int]]:
    """Each run of consecutive gap days, as (first day, last day)."""
    runs: list[tuple[int, int]] = []
    for r in rows:
        if r.gap is None:
            continue
        if runs and runs[-1][1] == r.day - 1:
            runs[-1] = (runs[-1][0], r.day)
        else:
            runs.append((r.day, r.day))
    return runs


def gap_musts(rows: Sequence[ComposedDay], run: tuple[int, int], lines: Sequence[Line],
              subjects: Sequence[Subject]) -> set[str]:
    """The subjects that were a must on some day of the gap run: a must on its own day with a non-empty `catchup`
    (statement 7). No notes are written inside a run, so a subject's tellings are those before it."""
    first, last = run
    told = {s.id: tellings(rows[:first], s.id) for s in subjects}
    return {s.id for d in range(first, last + 1) for s in showing(lines, subjects, d)
            if s.catchup and is_must(s, told[s.id])}


def own_notes(day: ComposedDay, subject_id: str) -> list[str]:
    return [n.slot for n in day.notes if n.subject == subject_id and n.slot in OWN_SLOTS]
