"""The checks past the sinks (dayone/sinkchecks.py) run over a played route's saves, so they run on any route and judge
day three's trips the day it has them: a card showing every need met starts when tapped, a tapped card lands when the
page draws it, a card paused dry has its supply's maker in reach. The saves are the route's, at most one per SAMPLE_S
and always each visit's exit. `judged` counts what the checks looked at, so a route showing nothing to judge reads as
blind and not as clean. Problems name ids and seconds only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Sequence
from dataclasses import dataclass

from ashfall_app.engine import RunBy, RunKind, Rules, Save, view
from tests.dayone import sinkchecks
from tests.dayone.player import DayOnePlayer

SAMPLE_S = 1800


@dataclass(frozen=True)
class Plumbing:
    judged: int
    """Cards looked at: shown ready, run by a tap, or paused, summed over the saves."""
    problems: tuple[str, ...]


def sampled(p: DayOnePlayer) -> list[Save]:
    """The route's saves from the opening's end: the first in each SAMPLE_S, and each visit's exit."""
    assert p.end_save is not None
    out, last = list[Save](), p.end_save.time - SAMPLE_S
    for s, _ in p.history:
        if s.time >= p.end_save.time and s.time - last >= SAMPLE_S:
            out.append(s)
            last = s.time
    return [*out, *(v.exit for v in p.visits if v.exit is not None)]


def check(saves: Sequence[Save], rules: Rules) -> Plumbing:
    judged, found = 0, list[str]()
    views = [view(s, rules) for s in saves]
    for s, v in zip(saves, views):
        judged += sum(1 for c in v.cards if c.blocker is None or c.by is RunBy.TAP or c.run is RunKind.PAUSED)
        found += [*sinkchecks.tap_fails(s, rules), *sinkchecks.tapped_landings(s, rules),
                  *sinkchecks.dry_unreached(s, rules)]
    _, broken = sinkchecks.needs_met_blocked(views)
    return Plumbing(judged, tuple(sorted({*found, *broken})))
