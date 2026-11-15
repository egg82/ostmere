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


def first_at(lines: Sequence[Line], subject: Subject, first_day: int, last_day: int) -> int | None:
    """The earliest `at` among the lines showing `subject` on days `first_day` .. `last_day` (statement 18), None when
    none does."""
    ats = [line.at for line in lines
           if line.source == subject.source and first_day * DAY_S <= line.at < (last_day + 1) * DAY_S]
    return min(ats) if ats else None


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
    """Each run of consecutive gap days, as (first day, last day); a gap day with notes (it broke off after writing)
    begins a run of its own (statement 9)."""
    runs: list[tuple[int, int]] = []
    for r in rows:
        if r.gap is None:
            continue
        if runs and runs[-1][1] == r.day - 1 and not r.notes:
            runs[-1] = (runs[-1][0], r.day)
        else:
            runs.append((r.day, r.day))
    return runs


def gap_musts(rows: Sequence[ComposedDay], run: tuple[int, int], lines: Sequence[Line],
              subjects: Sequence[Subject]) -> set[str]:
    """The subjects of a gap run caught up after it: one that showed on a run day with no note of it that day, has a
    non-empty `catchup`, and is a must by its tellings through the run (statements 7 and 9)."""
    first, last = run
    told = {s.id: tellings(rows[:last + 1], s.id) for s in subjects}
    return {s.id for d in range(first, last + 1) for s in showing(lines, subjects, d)
            if s.catchup and is_must(s, told[s.id]) and all(n.subject != s.id for n in rows[d].notes)}


def own_notes(day: ComposedDay, subject_id: str) -> list[str]:
    return [n.slot for n in day.notes if n.subject == subject_id and n.slot in OWN_SLOTS]
