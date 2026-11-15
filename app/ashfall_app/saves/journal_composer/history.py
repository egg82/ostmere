"""The save's lines read once per composed day: for each subject, the days it showed on, that day's line keys and its
earliest line's `at`; and the day's moments, in the order the lines were stored. A line whose source feeds no subject is
left out here, so nothing downstream can see it (statement 5)."""
from collections.abc import Sequence
from dataclasses import dataclass

from ..journal import DAY_S, Line, Subject


@dataclass(frozen=True)
class History:
    """Subject id to the days it showed on, each with its lines' keys (one per line), and to the earliest `at` among
    each day's lines."""

    by_subject: dict[str, dict[int, list[str]]]
    first: dict[str, dict[int, int]]

    def keys(self, subject: str, day: int) -> list[str]:
        return self.by_subject.get(subject, {}).get(day, [])

    def shows(self, subject: str, day: int) -> bool:
        return day in self.by_subject.get(subject, {})

    def first_at(self, subject: str, day: int) -> int:
        """The earliest `at` among the lines showing `subject` on `day`; only asked of a day it shows on."""
        return self.first[subject][day]


def read(lines: Sequence[Line], subjects: Sequence[Subject]) -> History:
    by_source = {s.source: s.id for s in subjects}
    by_subject: dict[str, dict[int, list[str]]] = {}
    first: dict[str, dict[int, int]] = {}
    for line in lines:
        sid = by_source.get(line.source) if line.source is not None else None
        if sid is not None:
            day = line.at // DAY_S
            by_subject.setdefault(sid, {}).setdefault(day, []).append(line.key)
            days = first.setdefault(sid, {})
            days[day] = min(days.get(day, line.at), line.at)
    return History(by_subject, first)


@dataclass(frozen=True)
class Moment:
    """A line of the day that weighs a subject: its first line of the day (`first`), or one carrying a key no earlier
    line of the subject held (`change`), or both."""

    subject: Subject
    first: bool
    change: bool


def moments(lines: Sequence[Line], subjects: Sequence[Subject], day: int) -> list[Moment]:
    """The day's moments, its lines by `at`, ties in the order `lines` holds them (statement 22)."""
    by_source = {s.source: s for s in subjects}
    fed = [(line, s) for line in lines if line.source is not None and (s := by_source.get(line.source)) is not None]
    held: dict[str, set[str]] = {}
    for line, s in fed:
        if line.at < day * DAY_S:
            held.setdefault(s.id, set()).add(line.key)
    today: set[str] = set()
    out: list[Moment] = []
    for line, s in sorted(((ln, s) for ln, s in fed if ln.at // DAY_S == day), key=lambda p: p[0].at):
        keys = held.setdefault(s.id, set())
        first, change = s.id not in today, line.key not in keys
        if first or change:
            out.append(Moment(s, first, change))
        today.add(s.id)
        keys.add(line.key)
    return out


def changed(history: History, subject: str, day: int) -> bool:
    """Statement 10's change: a key of the subject's lines on `day` that none of its lines held on an earlier day."""
    earlier = {k for d, keys in history.by_subject.get(subject, {}).items() if d < day for k in keys}
    return any(k not in earlier for k in history.keys(subject, day))


def run(history: History, subject: str, day: int) -> int:
    """The consecutive days ending at `day` on which the subject showed."""
    r = 0
    while history.shows(subject, day - r):
        r += 1
    return r


def showing(history: History, subjects: Sequence[Subject], day: int) -> list[Subject]:
    return [s for s in subjects if history.shows(s.id, day)]


def away(history: History, subjects: Sequence[Subject], day: int) -> bool:
    """Statement 13: an away gap runs into `day` from its start: a subject with `away_days = k` showed on one of the
    k - 1 days before it."""
    return any(history.shows(s.id, d) for s in subjects for d in range(day - s.away_days + 1, day))
