"""Keeper, tuner and the two control routes on one played route's visits (docs/design/worth-a-change.md, "What the
simulator measures").

Keeper is the route as played: its player changes the mix only where the chapter's moves make it (a card joining for
a need, a held trip, a greyed mix edited), never for a goal, which is the owner's play. The others see the same saves on the
same visits and each holds a mix of its own, scored in place of the player's own mix on the same set:
- tuner takes the best setup when its own falls behind it by the threshold (summary.is_moment);
- fresh takes the best setup at every visit, so its worth is how far the best moved since the visit before: the
  control where a change should be worth little;
- once takes the best setup at the first visit with a set and never changes it: the control where a change should be
  worth a lot, more so the further the game has moved.
The world is keeper's, so the routes say how often the best setup moves away from one taken earlier, not where a tuned
play would be by now.

A visit is read at its exit, the setup left running for the absence. Its causes are what changed since the visit
before's exit: an unlock of a kind the design's table names, a skill reaching its top, a prestige pick, a goal of the
visit before's set landing, the player's own mix edited, and the set gaining a skill. Ids and kinds only (CLAUDE.md,
"Never spoil the owner")."""
from dataclasses import dataclass

from ashfall_app.engine import Rules, Save, Unlock, UnlockKind, view
from ashfall_app.engine.phases import at_top
from tests.dayone.player import DayOnePlayer
from tests.worth import goaltime as gt
from tests.worth import probe as pr
from tests.worth.summary import VisitWorth, is_moment

CAUSE_OF = {UnlockKind.CARD: "card", UnlockKind.SKILL: "skill", UnlockKind.OFFER: "ask", UnlockKind.CHIP: "chore"}
"""The unlock kinds that are a cause in the design's table: a new card, a new skill row (its goals come into view),
an offer (a trip's supply or an ask), a chip (a chore)."""
CAUSES = ("goal landed", "card", "skill", "top", "prestige", "ask", "chore", "mix edited", "set grew")


@dataclass(frozen=True)
class Seen:
    """What a visit's causes are read against: the visit before's exit, its own mix and its set."""
    save: Save
    own: gt.Shares
    goals: tuple[gt.Goal, ...]


def causes(before: Seen, after: Save, own: gt.Shares, goals: tuple[gt.Goal, ...], rules: Rules,
           unlocked_at: dict[Unlock, int]) -> tuple[str, ...]:
    """What changed between two visits' exits, by kind, each kind once, in CAUSES' order."""
    t0, t1 = before.save.time, after.time
    found = {CAUSE_OF[u.kind] for u, t in unlocked_at.items() if t0 < t <= t1 and u.kind in CAUSE_OF}
    phases = {k.skill: k.phase.phase for k in before.save.skills}
    for k in after.skills:
        if k.phase.phase > phases.get(k.skill, k.phase.phase):
            found.add("prestige")
        elif at_top(after, rules, k.skill) and not at_top(before.save, rules, k.skill):
            found.add("top")
    levels = {str(b.skill): b.level for b in view(after, rules).skills}
    if any(levels.get(g.skill, 0) >= g.level for g in before.goals):
        found.add("goal landed")
    if own != before.own:
        found.add("mix edited")
    if {g.skill for g in goals} - {g.skill for g in before.goals}:
        found.add("set grew")
    return tuple(c for c in CAUSES if c in found)


def came_true(b: gt.Board, goals: tuple[gt.Goal, ...], shares: gt.Shares, left: Save, back: Save,
              rules: Rules) -> float | None:
    """XP the set's skills gained over the absence, as a fraction of what `shares`' rates at the exit promised."""
    r = gt.rates(b, shares)
    promised = sum(r.get(g.skill, 0.0) for g in goals) * (back.time - left.time)
    gained = sum(gt.xp(back, rules, g.skill)[0] - gt.xp(left, rules, g.skill)[0] for g in goals)
    return gained / promised if promised > 0 else None


def visit_worths(p: DayOnePlayer) -> list[VisitWorth]:
    """Each visit's scores on every route, from the opening's end to the edge, carried visit to visit."""
    rules, out = p.rules, list[VisitWorth]()
    held: dict[str, gt.Shares] = {}
    """Tuner's, fresh's and once's mixes, from the first visit with a set."""
    seen: Seen | None = None
    for i, visit in enumerate(p.visits):
        save = visit.exit
        assert save is not None
        b = gt.board(save, view(save, rules), rules)
        own = gt.own_mix(save)
        goals = pr.served(b, own)
        why = () if seen is None else causes(seen, save, own, goals, rules, p.unlocked_at)
        seen = Seen(save, own, goals)
        if not goals:
            out.append(VisitWorth(visit.index, save.time, 0, None, None, None, None, None, why, False, None))
            continue
        setups = {"keeper": own, "probe": pr.probe(rules, own, goals), **held}
        scores = {k: pr.score(b, goals, shares) for k, shares in setups.items()}
        best = min(s for s in scores.values() if s is not None)
        best_mix = setups[next(k for k, s in scores.items() if s == best)]
        tuner = scores.get("tuner", scores["keeper"])
        moment = is_moment(best, tuner)
        back = p.visits[i + 1].came if i + 1 < len(p.visits) else None
        out.append(VisitWorth(visit.index, save.time, len(goals), best, scores["keeper"], tuner,
                              scores.get("fresh", best), scores.get("once", best), why, moment,
                              None if back is None else came_true(b, goals, own, save, back, rules)))
        held = {"tuner": best_mix if moment else held.get("tuner", own), "fresh": best_mix,
                "once": held.get("once", best_mix)}
    return out
