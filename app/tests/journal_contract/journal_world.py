"""Plain builders for the journal composer's contract tests (ashfall_app/saves/journal.py), from its public types only.

Subjects carry their kind's required slots, keyed `<id>.<slot>.<n>`, and each source is the subject's own, so a line
shows exactly one subject. `PLAIN` habits make every non-must pass its write roll (care 1, diligence 1), leave the
budget wide and never busy, and switch late additions and misremembering off; a test changes only the knobs it is
about. `ref_roll` is the roll as `roll`'s docstring specifies it, used to choose save ids and to state expectations.
No Hypothesis here."""
import hashlib
from collections.abc import Callable, Iterable
from dataclasses import replace

from ashfall_app.saves.journal import (
    DAY_S, Band, ComposedDay, Fade, Gap, Habits, Line, Note, Press, Purpose, SlotName, Source, Subject, SubjectKind,
    compose_day,
)

PLAIN = Habits(
    routine=Fade(1.0, 1.0), worry=Press(1.0, 0.0), crowd=Fade(1.0, 1.0),
    floor=1.0, halflife=1.0, beat_refresh=0.0,
    lines_start=50, lines_floor=50, lines_halflife=1.0, busy_ratio=100.0,
    late_rate=0.0, misremember_rate=0.0, correct_after_days=1,
)
QUIET = replace(PLAIN, routine=Fade(0.0, 1.0), worry=Press(0.0, 0.0), crowd=Fade(0.0, 1.0))
"""No non-must ever passes its write roll: only musts, catch-ups, late additions and corrections are written."""

OWN_SLOTS: frozenset[SlotName] = frozenset({"first", "repeat", "mention", "misremember"})
TELLING_SLOTS: frozenset[SlotName] = frozenset({"first", "repeat", "catchup", "mention", "misremember"})


def keys(subject_id: str, slot: str, n: int) -> tuple[str, ...]:
    return tuple(f"{subject_id}.{slot}.{i}" for i in range(n))


def _subject(sid: str, kind: SubjectKind, source: Source, *, away: int = 0, repeat: int = 0, late: int = 0,
             misremember: int = 0, catchup: int = 1) -> Subject:
    return Subject(
        sid, kind, source, away_days=away, first=keys(sid, "first", 1), repeat=keys(sid, "repeat", repeat),
        catchup=keys(sid, "catchup", catchup), late=keys(sid, "late", late),
        misremember=keys(sid, "misremember", misremember), correction=keys(sid, "correction", misremember),
    )


def beat(sid: str, *, repeat: int = 0, late: int = 0, away: int = 0) -> Subject:
    return _subject(sid, "beat", Source("trigger", sid), away=away, repeat=repeat, late=late)


def person(sid: str, *, repeat: int = 0, late: int = 0) -> Subject:
    return _subject(sid, "person", Source("lane", sid, "joined"), repeat=repeat, late=late)


def routine(sid: str, *, repeat: int = 1, late: int = 0, misremember: int = 0, away: int = 0) -> Subject:
    return _subject(sid, "routine", Source("card", sid), away=away, repeat=repeat, late=late, misremember=misremember)


def worry(sid: str, *, repeat: int = 1, late: int = 0, away: int = 0) -> Subject:
    return _subject(sid, "worry", Source("trigger", sid), away=away, repeat=repeat, late=late, catchup=0)


def crowd(sid: str, *, bands: Iterable[tuple[int, int]] = ((1, 2), (3, 2)), late: int = 0) -> Subject:
    """A crowd of the `joined` way's mentions; `bands` are (at_least, number of keys)."""
    mention = tuple(Band(at, keys(sid, f"mention{at}", n)) for at, n in bands)
    return Subject(sid, "crowd", Source("mentions", None, "joined"), first=keys(sid, "first", 1), mention=mention,
                   late=keys(sid, "late", late))


def shows(subject: Subject, day: int, key: str | None = None, *, second: int = 0) -> Line:
    """A line showing `subject` on `day`, at that day's `second`; its key defaults to the subject's steady line."""
    return Line(key or f"{subject.id}.line", day * DAY_S + second, subject.source)


def noise(day: int, n: int = 0) -> Line:
    """A line that feeds no subject."""
    return Line(f"noise.{n}", day * DAY_S + n, None)


def row(day: int, *notes: Note, gap: Gap | None = None) -> ComposedDay:
    return ComposedDay(day, tuple(notes), gap)


def note(subject: Subject | str, slot: SlotName, n: int = 0, key: str | None = None) -> Note:
    """A note of `subject` by `slot`, its key the slot's n-th (`<id>.<slot>.<n>`) unless given."""
    sid = subject if isinstance(subject, str) else subject.id
    return Note(sid, slot, key or f"{sid}.{slot}.{n}")


def blanks(start: int, count: int) -> tuple[ComposedDay, ...]:
    return tuple(row(d) for d in range(start, start + count))


def lines_before(lines: Iterable[Line], day: int) -> tuple[Line, ...]:
    """The lines `compose_day` may be given for `day`: those before the day's end."""
    return tuple(line for line in lines if line.at < (day + 1) * DAY_S)


def compose_span(save_id: int, days: int, lines: Iterable[Line], subjects: Iterable[Subject],
                 habits: Habits = PLAIN, composed: tuple[ComposedDay, ...] = ()) -> tuple[ComposedDay, ...]:
    """Days `len(composed)` .. `days - 1` composed one at a time, each fed the rows before it, as the save writer
    does."""
    all_lines, subs, rows = tuple(lines), tuple(subjects), list(composed)
    for d in range(len(rows), days):
        rows.append(compose_day(save_id, d, lines_before(all_lines, d), tuple(rows), subs, habits))
    return tuple(rows)


def compose_next(save_id: int, composed: tuple[ComposedDay, ...], lines: Iterable[Line],
                 subjects: Iterable[Subject], habits: Habits = PLAIN) -> ComposedDay:
    """The day after `composed`, from hand-built rows."""
    day = len(composed)
    return compose_day(save_id, day, lines_before(lines, day), composed, tuple(subjects), habits)


def ref_roll(save_id: int, day: int, subject: str, purpose: Purpose) -> float:
    digest = hashlib.sha256(f"{save_id}|journal|{day}|{subject}|{purpose}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def find_save(wanted: Callable[[int], bool], start: int = 1) -> int:
    """The first save id from `start` for which `wanted` holds (rolls are uniform, so a band of width 0.05 is found
    within a few hundred ids)."""
    for save_id in range(start, start + 100_000):
        if wanted(save_id):
            return save_id
    raise AssertionError("no save id in range satisfies the condition")


def of(day: ComposedDay, subject: Subject | str) -> tuple[Note, ...]:
    sid = subject if isinstance(subject, str) else subject.id
    return tuple(n for n in day.notes if n.subject == sid)


def slots_of(day: ComposedDay, subject: Subject | str) -> list[SlotName]:
    return [n.slot for n in of(day, subject)]


def written_ids(day: ComposedDay) -> set[str]:
    return {n.subject for n in day.notes}
