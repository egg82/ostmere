"""A calendar day of play, counted by the absence ladder's own definition of a new thing (absence.counts): day n is the
24 h from (n - 1) days after the save's start (the convention of daytwo/abs_band.py), its arrivals are what appeared
between the saves at its two boundaries, and its lines are the played run's lines stamped inside it. Shared by the
week verdicts; `python -m tests.dayone.daily` prints week one's typical route."""
from collections import Counter
from collections.abc import Mapping, Sequence

from ashfall_app.engine import Line, Rules, Save, advance, view
from tests.dayone import absence
from tests.opening.playthrough import Player

DAY_S = 24 * 3600


def save_at(history: Sequence[tuple[Save, object]], rules: Rules, t: int) -> Save:
    """The play's save at engine time `t`: the last it passed through at or before `t`, run on to `t` (nobody decides in
    between, or the play would have a save there)."""
    before = [s for s, _ in history if s.time <= t]
    assert before, f"the play has no save at or before {t}"
    return before[-1] if before[-1].time == t else advance(before[-1], rules, t)


def day_counts(rules: Rules, history: Sequence[tuple[Save, object]], lines: Sequence[Line], first: int, days: int,
               text: Mapping[str, str] | None = None) -> list[Counter[str]]:
    """The arrivals by kind of each of `days` calendar days from engine time `first`; `text` is the lines' text where the
    shipped opening lacks a chapter's (absence.counts)."""
    edges = [save_at(history, rules, first + i * DAY_S) for i in range(days + 1)]
    seen = [view(s, rules) for s in edges]
    return [absence.counts(rules, seen[i], seen[i + 1], tuple(ln for ln in lines if edges[i].time <= ln.time < edges[i + 1].time), text)[0]
            for i in range(days)]


def whole_days(p: Player, end: int) -> int:
    """How many calendar days of the play are over by engine time `end`."""
    return (end - p.history[0][0].time) // DAY_S


def played(p: Player, end: int, text: Mapping[str, str] | None = None) -> list[Counter[str]]:
    """Each whole calendar day of `p` up to `end`."""
    return day_counts(p.rules, p.history, p.lines, p.history[0][0].time, whole_days(p, end), text)


def alive(c: Counter[str]) -> bool:
    """A day is alive with an arrival of any kind but a line: lines alone do not keep it so."""
    return any(n > 0 for k, n in c.items() if k != "line")


def empty_days(found: Sequence[Counter[str]]) -> list[int]:
    """The 1-based days with no arrival but lines."""
    return [i + 1 for i, c in enumerate(found) if not alive(c)]


def lines_of(found: Sequence[Counter[str]]) -> list[str]:
    out = ["day " + " ".join(f"{k:>7s}" for k in absence.KINDS) + "  total"]
    out += [f"{i + 1:3d} " + " ".join(f"{c[k]:7d}" for k in absence.KINDS) + f"  {sum(c.values()):5d}" for i, c in enumerate(found)]
    return out
