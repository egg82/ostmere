"""What day two's stores lose to their caps (tests/dayone/absence/caploss.py) over a played route and over absences from its
last decision, nobody deciding, on day two's rules alone. Store ids only (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import dataclass

from tests.daytwo import checks
from tests.daytwo import content as c
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.absence import caploss


@dataclass(frozen=True)
class DayTwoLoss:
    played: dict[str, caploss.StoreLoss]
    """B3 to the last decision, run on between the route's decisions."""
    away: dict[int, dict[str, caploss.StoreLoss]]
    """From the last decision, for each of caploss.ABSENCE_H."""


def day_two_loss(p: DayTwoPlayer) -> DayTwoLoss:
    rules = c.rules2()
    b3 = checks.b3_at(p)
    history = [s for s, _ in p.history if s.time >= b3]
    assert len(history) > 1, "no decision after B3"
    tally = caploss.Tally()
    caploss.between(history, rules, tally)
    return DayTwoLoss(tally.losses(), caploss.absences(history[-1], rules))


def lines_of(name: str, found: DayTwoLoss) -> list[str]:
    """The report's rows: one per store and span, the share of its making the cap dropped."""
    out = [f"  lost to caps, {name}: share of each store's making dropped at its cap"]
    spans = [("played", found.played)] + [(f"away {h} h", found.away[h]) for h in caploss.ABSENCE_H]
    for label, losses in spans:
        shares = " ".join(f"{s} {100 * v.share:.0f}%" for s, v in losses.items() if v.lost)
        out.append(f"    {label:9s} all {100 * caploss.total_share(losses):3.0f}%  {shares}")
    return out
