"""The set of goals a visit is scored on, a setup's score on it, and the probe mix cut to serve it
(docs/design/worth-a-change.md, "What the simulator measures"). Pure: the caller supplies the board (goaltime.py).

The set is the open goals that are a choice (the goal's card alone lands it at least CHOICE_S out) on skills the
player's own mix trains now. A setup's score is the time until every goal of the set has landed; a setup that leaves
one unserved never lands them all (None).

The probe keeps the player's mix's cards that train no skill (upkeep, such as rest) at their shares and splits the rest
of the hands between the set's cards in proportion to each card's time alone, t_i. Shares s_i land goal i at t_i / s_i,
so the last lands soonest when all land together, at sum(t_i): the time one card after another would take, so a mix
and a queue of stints score alike."""
from collections.abc import Sequence

from ashfall_app.engine import BP, Rules
from tests.dayone.goals import CHOICE_S
from tests.worth.goaltime import Board, Goal, Shares, rates


def served(b: Board, own: Shares) -> tuple[Goal, ...]:
    """The goals a setup is scored on, soonest alone first."""
    trained = rates(b, own)
    return tuple(sorted((g for g in b.goals if g.alone_s >= CHOICE_S and trained.get(g.skill, 0.0) > 0),
                        key=lambda g: (g.alone_s, g.skill)))


def score(b: Board, goals: Sequence[Goal], shares: Shares) -> float | None:
    """Seconds until every goal of the set has landed with `shares` running; None when one never does."""
    assert goals, "a score needs a goal"
    r = rates(b, shares)
    if any(r.get(g.skill, 0.0) <= 0 for g in goals):
        return None
    return max(g.xp_left / r[g.skill] for g in goals)


def fixed(rules: Rules, own: Shares) -> Shares:
    """The player's mix's cards that train no skill, at their shares."""
    skilled = {str(c.id) for c in rules.cards if c.skill is not None}
    return tuple((c, bp) for c, bp in own if c not in skilled)


def split(alone: Sequence[float], free_bp: int) -> list[int]:
    """Shares in basis points out of `free_bp`, in proportion to `alone`, the remainder to the longest."""
    shares = [int(free_bp * t / sum(alone)) for t in alone]
    shares[alone.index(max(alone))] += free_bp - sum(shares)
    return shares


def probe(rules: Rules, own: Shares, goals: Sequence[Goal]) -> Shares:
    """The player's upkeep cards as they are, and the rest of the hands split between the set's cards."""
    keep = fixed(rules, own)
    shares = split([g.alone_s for g in goals], BP - sum(bp for _, bp in keep))
    return tuple(sorted((*keep, *((g.card, bp) for g, bp in zip(goals, shares) if bp))))


def one_card(rules: Rules, own: Shares, goals: Sequence[Goal]) -> Shares:
    """The first build's best probe, kept as a control: the soonest goal's card on all of the hands the upkeep leaves."""
    keep = fixed(rules, own)
    return tuple(sorted((*keep, (goals[0].card, BP - sum(bp for _, bp in keep)))))
