"""What earlier days owe the day being composed: the catch-ups of the gap run just ended (statement 9), the late
additions drawn yesterday (16) and the corrections now due (17)."""
from collections.abc import Sequence

from ..journal import ComposedDay, Habits, Subject, roll
from .history import History, showing
from .ledger import gap_run, tellings
from .telling import Telling, is_must, plain


def catchups(composed: Sequence[ComposedDay], history: History, subjects: Sequence[Subject]) -> list[Telling]:
    """Each must of the gap run just ended, once, by the earliest line it showed by in the run, then id."""
    first_at: dict[str, int] = {}
    for d in gap_run(composed):
        for s in showing(history, subjects, d):
            first_at.setdefault(s.id, history.first_at(s.id, d))
    by_id = {s.id: s for s in subjects}
    out: list[Telling] = []
    for sid in sorted(first_at, key=lambda i: (first_at[i], i)):
        t = plain(by_id[sid], "catchup")
        if t is not None and is_must(by_id[sid], tellings(composed, sid)):
            out.append(t)
    return out


def lates(save_id: int, composed: Sequence[ComposedDay], subjects: Sequence[Subject], habits: Habits) -> list[Telling]:
    """Late additions for the subjects written yesterday by a slot but late or correction, whose late roll passed."""
    if not composed:
        return []
    yesterday = composed[-1]
    wrote = {n.subject for n in yesterday.notes if n.slot not in ("late", "correction")}
    out: list[Telling] = []
    for s in sorted(subjects, key=lambda x: x.id):
        t = plain(s, "late")
        if t is not None and s.id in wrote and roll(save_id, yesterday.day, s.id, "late") < habits.late_rate:
            out.append(t)
    return out


def corrections(composed: Sequence[ComposedDay], subjects: Sequence[Subject], habits: Habits,
                day: int) -> list[Telling]:
    """The corrections due by `day` and not yet written, by subject id."""
    out: list[Telling] = []
    for s in sorted(subjects, key=lambda x: x.id):
        t = plain(s, "correction")
        if t is not None and _due(composed, s.id, habits.correct_after_days, day):
            out.append(t)
    return out


def _due(composed: Sequence[ComposedDay], subject: str, wait: int, day: int) -> bool:
    wrong = [r.day for r in composed for n in r.notes if n.subject == subject and n.slot == "misremember"]
    if not wrong or wrong[-1] + wait > day:
        return False
    return not any(n.subject == subject and n.slot == "correction" for r in composed[wrong[-1] + 1:] for n in r.notes)
