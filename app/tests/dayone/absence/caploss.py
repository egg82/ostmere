"""What each store's makers make past its cap ("lost to caps", docs/design/banked-time-plan.md, "Measured"). From a
save and its rules, each unlocked store's ledger line is read over a span with nobody deciding (`run`) or between a
played route's decisions (`between`). Made is the positive contributions; lost is the
line's net while the store sits at its cap, the overflow the cap drops. XP still trains at a cap, so this counts
materials only. Amounts are rate units times seconds (a rate of r over s seconds is r * s), so a figure is
comparable across stores and spans. Store ids only (CLAUDE.md, "Never spoil the owner").

The span is walked event to event (the engine's `next_event`): every rate, and whether a store sits at its cap, is
constant between two events, so each stretch is counted exactly with no sampling step. A store reaching its cap is an
event (STORE_LIMIT), and so is a card's work running out, so a short lump stops counting where it stops.
"""
from collections.abc import Sequence
from dataclasses import dataclass, field

from ashfall_app.engine import LedgerLine, Rules, Save, advance, value_at, view

ABSENCE_H = (8, 24, 72)
"""The absences the reports and the check read, in hours."""
HOUR_S = 3600


@dataclass(frozen=True)
class StoreLoss:
    made: int
    lost: int

    @property
    def share(self) -> float:
        """The fraction of what the store made that the cap dropped; 0 when it made nothing."""
        return self.lost / self.made if self.made else 0.0


@dataclass
class Tally:
    """Made and lost per store id, summed over every sample added."""

    made: dict[str, int] = field(default_factory=dict[str, int])
    lost: dict[str, int] = field(default_factory=dict[str, int])

    def add(self, store: str, made: int, lost: int) -> None:
        self.made[store] = self.made.get(store, 0) + made
        self.lost[store] = self.lost.get(store, 0) + lost

    def losses(self) -> dict[str, StoreLoss]:
        """Per store; fails when nothing was sampled, since a tally of nothing would report no loss anywhere."""
        assert self.made, "no store was sampled"
        return {s: StoreLoss(self.made[s], self.lost[s]) for s in sorted(self.made)}


def at_cap(line: LedgerLine, now: int) -> bool:
    return value_at(line.segment, now) >= line.cap


def stretch(ledger: Sequence[LedgerLine], now: int, end: int, tally: Tally) -> None:
    """Made and lost per store from `now` to `end`, which is no later than the next event, on the ledger read at `now`."""
    seconds = end - now
    for line in ledger:
        made = sum(c.per_hour for c in line.contributions if c.per_hour > 0) * seconds
        lost = line.net_per_hour * seconds if at_cap(line, now) and line.net_per_hour > 0 else 0
        tally.add(str(line.store), made, lost)


def run(save: Save, rules: Rules, until: int, tally: Tally) -> Save:
    """The save advanced to `until` with nobody deciding, counted event to event; returns the save at `until`."""
    while save.time < until:
        read = view(save, rules)
        end = until if read.next_event is None else min(read.next_event.time, until)
        stretch(read.ledger, save.time, end, tally)
        save = advance(save, rules, end)
    return save


def between(history: Sequence[Save], rules: Rules, tally: Tally) -> None:
    """A played route's history (the save after each decision), each gap between two run on as nobody deciding."""
    for a, b in zip(history, history[1:]):
        run(a, rules, b.time, tally)


def absences(save: Save, rules: Rules, hours: Sequence[int] = ABSENCE_H) -> dict[int, dict[str, StoreLoss]]:
    """Loss over each absence from `save`, nobody deciding; each is stepped on from the shorter (hours ascending)."""
    out: dict[int, dict[str, StoreLoss]] = {}
    tally, at = Tally(), save
    for h in hours:
        at = run(at, rules, save.time + h * HOUR_S, tally)
        out[h] = tally.losses()
    return out


def total_share(losses: dict[str, StoreLoss]) -> float:
    """Lost over made across every sampled store."""
    made = sum(s.made for s in losses.values())
    return sum(s.lost for s in losses.values()) / made if made else 0.0
