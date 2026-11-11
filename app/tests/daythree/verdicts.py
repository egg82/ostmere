"""Day three's checks on a played route (docs/design/day-three-plan.md, item 7; docs/design/sim-invariants.md): what
each gathered store loses to its cap away from the route's last decision (dayone/capcheck.py), the checks past the
sinks over its saves (plumbing.py), and the 2 AM test across the chapter; and the counts the readout prints (report.py)
for every visit from the one B4 is seen in. Ids and numbers only (CLAUDE.md, "Never spoil the owner")."""
from functools import cache

from ashfall_app.engine import Verb
from tests.daythree import content as c3
from tests.daythree import counters, plumbing, visits
from tests.daythree.routes import day3
from tests.daytwo.player import QUEUEABLE, DayTwoPlayer, visit_seen
from tests.dayone import capcheck
from tests.dayone.parity import Measured, Present, babysat, replay

BOOSTS = (*QUEUEABLE, *c3.COMFORTS)
"""What the babysitter taps the second it can: day two's queueable steps and day three's comforts."""
AFTER_B5_S = 3600
NOT_WAITS = ("cure_hearth",)
"""Work the hearth's chain needs, not a wait the player chose: a return during it is not marked as a long wait
(content/team/day-three-numbers.md, "Targets: per visit")."""


def b4_visit(p: DayTwoPlayer) -> int:
    found = visit_seen(p.visits, p.seen_at.get("B4"))
    assert found is not None, "B4 was seen"
    return found


def chapter_counts(p: DayTwoPlayer) -> list[counters.Counts]:
    return [counters.count(v, p.rules) for v in visits.visits_of(p)][b4_visit(p) - 1:]


def cap_loss(p: DayTwoPlayer) -> dict[str, tuple[int, ...]]:
    camp = c3.opening3().camp
    return capcheck.failing(p.history[-1][0], p.rules, (camp.store,) if camp else ())


def start(p: DayTwoPlayer) -> int:
    """The exit of the visit before the one B4 is seen in: where the chapter's replay starts."""
    return p.visits[b4_visit(p) - 2].end


@cache
def two_am3(seed: int = 0) -> tuple[Measured, Measured]:
    """The whenever player's decisions from the chapter's start replayed as they were and as a babysitter given the same
    reveals, to an hour past B5."""
    w = day3("whenever", seed)
    t = start(w)
    i = next(i for i, (s, _) in enumerate(w.history) if s.time >= t)
    s0 = w.history[i][0]
    log: list[tuple[int, Verb]] = [(at, verb) for at, _, verb in w.decisions if at >= s0.time]
    present = Present.of(tuple((v.start, v.end) for v in w.visits), log)
    end = w.landed_at["B5"] + AFTER_B5_S
    return (replay(w.rules, s0, log, end, False, boosts=BOOSTS),
            replay(w.rules, s0, babysat(log), end, True, present, BOOSTS))


def plumbed(p: DayTwoPlayer) -> plumbing.Plumbing:
    return plumbing.check(plumbing.sampled(p), p.rules)
