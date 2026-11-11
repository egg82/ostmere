"""How far one decision moves what the player finds at the next return (counters.py, "decide"), read off the saves just
before and after it, each run on to that return with nobody deciding: a fight's odds, a goal's landing, a capped
store's level. One pass over each path reads all three (the engine's run-on is the cost); the counter turns each number
into a yes or no with the thresholds in counters.py. Numbers and ids only (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import dataclass

from ashfall_app.engine import CardId, Rules, Save, advance, value_at, view
from ashfall_app.engine.work import completions
from tests.daythree.landings import HORIZON_S, goals

GRID_S = 1800
"""The spacing a path is read at: odds and landings are read to this."""


@dataclass(frozen=True)
class Shift:
    odds_bp: int
    """The largest change in a fight's loss share (basis points of fights lost): its absolute difference between the two
    paths, averaged over the reads of the absence."""
    finish_s: int
    """The largest change in when a goal on offer next lands; one not landed by landings.HORIZON_S lands there."""
    level_bp: int
    """The largest change in a capped store's level at the return, in basis points of its cap."""


@dataclass(frozen=True)
class Path:
    """One save run on to the return."""

    loss: tuple[dict[str, int], ...]
    """Each fight's loss share at each read."""
    landed: dict[CardId, int]
    """When each goal first completed once more, else landings.HORIZON_S after the decision."""
    level: dict[str, int]
    """Each capped store's level at the return, in basis points of its cap."""


def loss_shares(save: Save, rules: Rules) -> dict[str, int]:
    return {f.runner: f.loss_bp for f in view(save, rules).fights}


def levels(save: Save, rules: Rules) -> dict[str, int]:
    return {str(ln.store): value_at(ln.segment, save.time) * 10_000 // ln.cap for ln in view(save, rules).ledger if ln.cap > 0}


def reads(start: int, until: int) -> list[int]:
    """The times a path is read at: every GRID_S after `start`, then `until`."""
    return [*range(start + GRID_S, until, GRID_S), until]


def run_on(save: Save, rules: Rules, cards: tuple[CardId, ...], until: int) -> Path:
    """The save read at each time up to `until` (odds, landings), its levels at `until`, then on to HORIZON_S after it
    (landings only)."""
    base = {c: completions(save, rules, c) for c in cards}
    landed: dict[CardId, int] = {}
    loss: list[dict[str, int]] = []
    s, end = save, max(until, save.time + HORIZON_S)
    lv: dict[str, int] = {}
    for t in [*reads(save.time, until), *range(until + GRID_S, end, GRID_S)]:
        s = advance(s, rules, t)
        if t <= until:
            loss.append(loss_shares(s, rules))
        if t == until:
            lv = levels(s, rules)
        landed.update({c: t for c in cards if c not in landed and completions(s, rules, c) > base[c]})
    return Path(tuple(loss), {c: landed.get(c, end) for c in cards}, lv)


def gap(a: dict[str, int], b: dict[str, int]) -> int:
    """The largest difference between two readings of the same names (a name read in one only counts from 0)."""
    return max((abs(a.get(k, 0) - b.get(k, 0)) for k in a.keys() | b.keys()), default=0)


def mean_gap(a: tuple[dict[str, int], ...], b: tuple[dict[str, int], ...]) -> int:
    """Each name's absolute difference averaged over the reads; the largest."""
    names = {k for x in (*a, *b) for k in x}
    return max((sum(abs(x.get(k, 0) - y.get(k, 0)) for x, y in zip(a, b)) // max(len(a), 1) for k in names), default=0)


def shift(before: Save, after: Save, rules: Rules, until: int) -> Shift:
    """Both paths run on from the decision to `until`, the next return."""
    cards = goals(before, rules)
    a, b = run_on(before, rules, cards, until), run_on(after, rules, cards, until)
    return Shift(mean_gap(a.loss, b.loss), max((abs(a.landed[c] - b.landed[c]) for c in cards), default=0),
                 gap(a.level, b.level))
