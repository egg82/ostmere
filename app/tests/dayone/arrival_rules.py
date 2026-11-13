"""The arrival queue's timing rules, read from the page's own source so the simulator and the page share one home:
the pace and cap from client/src/game/arrivals.ts, the reading time from client/src/game/reading.ts, and the line kinds
the story strip plays from client/src/game/chronicle.ts. `reveal_ms` is
ArrivalQueue.start's schedule for one batch without reduced motion: lines first, each holding the next turn for its
reading time, then the rest evenly within the cap, the ledger's lines holding the kinds behind them (skills, cards) for
their longest reading time."""
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

GAME = Path(__file__).resolve().parents[2] / "client" / "src" / "game"


@dataclass(frozen=True)
class Pace:
    min_gap_ms: int
    max_gap_ms: int
    cap_ms: int
    wpm: int
    floor_ms: int


def _number(src: str, pattern: str) -> int:
    found = re.search(pattern, src)
    assert found is not None, f"the page source no longer matches {pattern!r}"
    return int(found.group(1))


@cache
def pace() -> Pace:
    arrivals, reading = (GAME / "arrivals.ts").read_text(), (GAME / "reading.ts").read_text()
    return Pace(
        _number(arrivals, r"export const MIN_GAP_MS = (\d+);"), _number(arrivals, r"export const MAX_GAP_MS = (\d+);"),
        _number(arrivals, r"export const CAP_MS = (\d+);"), _number(reading, r"wpm:\s*(\d+)"),
        _number(reading, r"floorMs:\s*(\d+)"))


@cache
def strip_kinds() -> frozenset[str]:
    """The kinds chronicle.ts ROUTES to the Story filter: the only lines the strip plays (its inStrip)."""
    src = (GAME / "chronicle.ts").read_text()
    block = re.search(r"export const ROUTES[^{]*\{([^}]*)\}", src)
    assert block is not None, "the page source no longer has its ROUTES table"
    routes = dict(re.findall(r'(\w+): "(\w+)"', block.group(1)))
    assert len(routes) >= 6, f"ROUTES read as {routes}"
    return frozenset(kind for kind, f in routes.items() if f == "story")


def reading_ms(text: str) -> int:
    p = pace()
    return max(p.floor_ms, math.floor(len(text.split()) / p.wpm * 60_000 + 0.5))


def gap_ms(rest: int) -> float:
    p = pace()
    return 0 if rest < 2 else min(p.max_gap_ms, max(p.min_gap_ms, p.cap_ms / (rest - 1)))


def squeezed(rest: int) -> int:
    """How many of `rest` non-line arrivals the cap makes share the last turn instead of keeping the pace's gap."""
    return sum(1 for i in range(rest) if i * gap_ms(rest) > pace().cap_ms)


def reveal_ms(holds_ms: Sequence[int], rest: int, ledger_ms: Sequence[int] = (), behind: int = 0) -> int:
    """From the first turn to the last arrival's: the lines' reading times, then the rest's spread. `ledger_ms`: the
    reading holds of the ledger lines among `rest`; `behind`: how many of `rest` come after them in kind order, which
    wait out the longest hold in place of one gap."""
    gap = gap_ms(rest)
    last = min(pace().cap_ms, (rest - 1) * gap) if rest else 0
    held = max(0.0, max(ledger_ms, default=0) - gap) if behind > 0 else 0
    return round(sum(holds_ms) + last + held)
