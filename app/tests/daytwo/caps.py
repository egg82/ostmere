"""What day two's stores lose to their caps (tests/dayone/caploss.py) over a played route and over absences from its
last decision, nobody deciding: on day two's rules alone, and from day two's end on the shipped chapters, where the
check reads (verdicts.py). Store ids only (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import dataclass

from ashfall_app.engine import Save
from tests.daythree import content as c3
from tests.daytwo import checks
from tests.daytwo import content as c
from tests.daytwo.player import DayTwoPlayer, visit_seen
from tests.dayone import capcheck, caploss


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


def cap_loss_failing(p: DayTwoPlayer) -> dict[str, tuple[int, ...]]:
    """The gathered stores losing too much to their caps over an absence from the route's last decision, on day two's
    rules alone (no chapter after it)."""
    camp = c.opening2().camp
    assert p.history, "no decision was played"
    return capcheck.failing(p.history[-1][0], c.rules2(), (camp.store,) if camp else ())


def shipped_end(p: DayTwoPlayer) -> Save:
    """Day two's end as a player has it: the last decision of the visit B4 is seen in, on a play with the chapters
    after it merged (daythree/routes.py), so what the page offers from B4 on is there."""
    seen = visit_seen(p.visits, p.seen_at.get("B4"))
    assert seen is not None, "B4 was seen"
    end = p.visits[seen - 1].end
    return [s for s, _ in p.history if s.time <= end][-1]


def shipped_cap_loss_failing(p: DayTwoPlayer) -> dict[str, tuple[int, ...]]:
    """The gathered stores losing too much to their caps over an absence from day two's end on the shipped chapters
    (`p`: a play of them, daythree/routes.day3)."""
    camp = c3.opening3().camp
    return capcheck.failing(shipped_end(p), p.rules, (camp.store,) if camp else ())
