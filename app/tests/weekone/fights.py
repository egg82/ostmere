"""Combat's timing and preparation checks over week one (docs/design/combat-plan.md, item 9). The typical route's decisions
from the start of day four are replayed to an hour past G2 (verdicts.two_am_week's span) with the visits sliced differently
(engine invariant 81, "Timing does not matter"), and with the week's gear never built. Ids and numbers only."""
from collections.abc import Iterable
from functools import cache
from dataclasses import dataclass, fields

from ashfall_app.engine import InvalidVerbError, Rules, Save, SetQueue, TapCard, Verb, advance, decide, view
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.schedules import schedule
from tests.weekone import content as w1
from tests.weekone import verdicts
from tests.weekone.routes import HORIZON_S, week1

GEAR = frozenset({w1.WOODSHED, w1.HEARTH_STONES, w1.SPEAR, w1.BEDDING})
"""The week's gear: the builds that raise the hunters' side."""
LOSS_RATIO = (3, 4)
"""The hunt, with the gear built, loses at most this share of the hunts it loses without it."""
Log = list[tuple[int, Verb]]


@dataclass(frozen=True)
class Week:
    start: Save
    log: Log
    end: int
    rules: Rules


@cache
def week(name: str = "typical") -> Week:
    """`name`'s decisions from the start of day four, and the hour past G2 they are played to."""
    p: DayTwoPlayer = week1(name)
    t = verdicts.start(p)
    s0 = next(s for s, _ in p.history if s.time >= t)
    return Week(s0, [(at, v) for at, _, v in p.decisions if at >= s0.time],
                p.landed_at[p.stop_beat()] + verdicts.AFTER_END_S, p.rules)


def visit_edges(name: str, seed: int, w: Week) -> list[int]:
    """The starts and ends of `name`'s visits that fall inside the week's span."""
    base = week1("typical").history[0][0].time
    found = [x for v in schedule(name, 0, seed, HORIZON_S).visits for x in (v.start, v.start + v.length)]
    return [base + x for x in found if w.start.time < base + x < w.end]


def run(w: Week, log: Log, stops: Iterable[int] = (), strict: bool = True) -> Save:
    """`log` applied at its times from the week's start to its end, advancing and reading the view at each of `stops`
    on the way. A verb that no longer fits is skipped unless `strict`."""
    s, i = w.start, 0
    for t in sorted({*stops, *(at for at, _ in log if at < w.end), w.end}):
        while i < len(log) and log[i][0] <= s.time:
            s, i = _apply(s, w.rules, log[i][1], strict), i + 1
        s = advance(s, w.rules, t)
        view(s, w.rules)
    while i < len(log) and log[i][0] <= s.time:
        s, i = _apply(s, w.rules, log[i][1], strict), i + 1
    return s


@cache
def unsliced() -> Save:
    """The typical week played on its decisions alone."""
    w = week()
    return run(w, w.log)


def _apply(s: Save, rules: Rules, verb: Verb, strict: bool) -> Save:
    try:
        return decide(s, rules, s.time, verb)
    except InvalidVerbError:
        if strict:
            raise
        return s


def without_gear(log: Log) -> Log:
    """`log` with every tap and queue entry of the week's gear taken out."""
    out: Log = []
    for at, v in log:
        if isinstance(v, TapCard) and v.card in GEAR:
            continue
        if isinstance(v, SetQueue):
            v = SetQueue(tuple(e for e in v.entries if not (isinstance(e.verb, TapCard) and e.verb.card in GEAR)))
        out.append((at, v))
    return out


def built_gear(log: Log) -> bool:
    return without_gear(log) != log


def hunts(s: Save, rules: Rules) -> tuple[int, int]:
    """(fought, lost) of the hunt at `s`."""
    f = next(f for f in view(s, rules).fights if f.runner == w1.HUNT)
    return f.fought, f.lost


def differing(a: Save, b: Save) -> list[str]:
    """The Save fields on which two saves differ."""
    return [f.name for f in fields(a) if getattr(a, f.name) != getattr(b, f.name)]
