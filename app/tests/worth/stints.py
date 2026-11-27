"""The worth readout's route with its own rules: a goal stint per goal of a visit's set, against keeper's offers only
(docs/design/worth-a-change.md, "What the simulator measures"). Unlike the other routes it does not score a mix by its
rates: it plays the real engine on the save a visit left, once as keeper left it and once with the stints queued,
and reads how far the set got in two days.

Keeper writes no rule for a goal (route.py). The stints route queues, ahead of whatever keeper's queue holds, one entry
per goal of the set, soonest alone first: a mix of the player's upkeep cards (probe.fixed) and the goal's card on the
hands that leave, run until the goal row's `until` holds (api goalrows, contract/goal-stints.txt "Goal stints"); the engine pops it
there and the player's own mix runs on. Both plays leave the world as it is: nothing is tapped after the exit. Ids and
kinds only (CLAUDE.md, "Never spoil the owner")."""
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from ashfall_app.api.goals import goal_models as gm
from ashfall_app.api.convert import from_condition
from ashfall_app.api.goals.goalrows import goal_rows
from ashfall_app.engine import (
    BP, CardId, CardShare, Condition, Mix, MixId, QueueEntry, Rules, Save, SaveMix, SetQueue, SwitchMix, advance, decide,
    view,
)
from ashfall_app.engine.orders.conditions import is_true
from tests.dayone.player.player import DayOnePlayer
from tests.worth import goaltime as gt
from tests.worth import probe as pr
from tests.worth import summary as sm

WINDOW_S = 2 * sm.DAY_S
"""How far past a visit's exit each setup is played: the engine's cost grows with the span it plays, and the goals of a
set are hours to days out."""
EVERY_DAYS = 3
"""The days read are the second, then every this many."""
SAME = 0.005
"""Two setups' shares within this of each other read as the same."""


@dataclass(frozen=True)
class Window:
    """What a setup did to a set over the window after a visit's exit."""
    done: float
    """The share of the set's XP still to go at the exit that the window brought (each goal capped at its own)."""
    landed: int
    """Goals of the set that hold at the window's end."""


@dataclass(frozen=True)
class StintWorth:
    index: int
    at: int
    goals: int
    keeper: Window
    """The save as keeper left it: the player's mix, the rules and queue it holds, nothing queued for a goal."""
    stints: Window
    """The same save with a stint queued per goal of the set."""


def stint_mix(rules: Rules, own: gt.Shares, goal: gt.Goal) -> Mix:
    """The player's upkeep cards at their shares and the goal's card on the hands that leave."""
    keep = pr.fixed(rules, own)
    shares = (*keep, (goal.card, BP - sum(bp for _, bp in keep)))
    return Mix(MixId(f"stint:{goal.skill}"), tuple(CardShare(CardId(c), bp) for c, bp in shares))


def level_untils(save: Save, rules: Rules, goals: Sequence[gt.Goal]) -> list[Condition]:
    """The condition that holds once each goal has landed, as the goal's row words it."""
    rows = {(r.skill, r.target): r for r in goal_rows(save, rules, view(save, rules), []) if r.kind is gm.GoalKind.LEVEL}
    return [from_condition(rows[(g.skill, g.level)].until, rules) for g in goals]


def with_stints(save: Save, rules: Rules, own: gt.Shares, goals: Sequence[gt.Goal], untils: Sequence[Condition]) -> Save:
    """`save` with each goal's mix saved and queued until the goal lands, ahead of the queue it already holds."""
    entries: list[QueueEntry] = []
    for goal, until in zip(goals, untils):
        mix = stint_mix(rules, own, goal)
        save = decide(save, rules, save.time, SaveMix(mix))
        entries.append(QueueEntry(SwitchMix(mix.id), until))
    return decide(save, rules, save.time, SetQueue((*entries, *save.queue)))


def played(save: Save, rules: Rules, goals: Sequence[gt.Goal], untils: Sequence[Condition]) -> Window:
    """`save` advanced through the real engine for the window, read against the set it had at the exit."""
    later = advance(save, rules, save.time + WINDOW_S)
    left = [g.xp_left for g in goals]
    gained = [min(gt.xp(later, rules, g.skill)[0] - gt.xp(save, rules, g.skill)[0], g.xp_left) for g in goals]
    return Window(sum(gained) / sum(left), sum(is_true(later, rules, c) for c in untils))


def stint_worths(p: DayOnePlayer) -> list[StintWorth]:
    """The first visit with a set on every third day from the second, to the edge, each played as keeper left it and
    with stints. A play costs the span it plays through, so a day's visit is paid in tens of seconds."""
    rules, out = p.rules, list[StintWorth]()
    days: set[int] = set()
    for visit in p.visits:
        save = visit.exit
        assert save is not None
        day = sm.day_of(save.time)
        if day in days or (day - 2) % EVERY_DAYS:
            continue
        own = gt.own_mix(save)
        goals = pr.served(gt.board(save, view(save, rules), rules), own)
        if not goals:
            continue
        days.add(day)
        untils = level_untils(save, rules, goals)
        out.append(StintWorth(visit.index, save.time, len(goals), played(save, rules, goals, untils),
                              played(with_stints(save, rules, own, goals, untils), rules, goals, untils)))
    return out


def verdict(v: StintWorth) -> str:
    """Which setup brings the set closer over the window."""
    d = v.stints.done - v.keeper.done
    return "stints ahead" if d > SAME else "stints behind" if d < -SAME else "same"


def text(p: DayOnePlayer, route: str) -> str:
    visits = stint_worths(p)
    assert visits, "no visit with a goal to read"
    counts = Counter(verdict(v) for v in visits)
    rows = [f"  V{v.index:<4d}{v.at / sm.DAY_S:6.2f}  {v.goals:4d}   {v.keeper.done * 100:4.0f}%  {v.keeper.landed:2d}"
            f"   {v.stints.done * 100:4.0f}%  {v.stints.landed:2d}   {verdict(v)}" for v in visits]
    days = WINDOW_S // sm.DAY_S
    return "\n".join([
        f"== worth with a route's own rules on {route}: goal stints against offers only, on the real engine",
        "  from the exit of the first visit with a set on days 2, 5, 8, ... (the worth readout's set), the save is played",
        f"  {days} days as keeper left it (offers only: no rule written for a goal) and with a stint queued per goal of the",
        "  set (soonest alone first: the upkeep and the goal's card, until the goal lands, then the player's mix);",
        "  nothing is tapped after the exit. done: the share of the set's XP still to go at the exit that the play",
        "  brought; landed: goals of the set that hold at its end",
        "  visits by which setup is ahead: " + ", ".join(f"{k} {n}" for k, n in sorted(counts.items())),
        "  visit   day  goals  keeper: done, landed  stints: done, landed",
        *rows,
    ]) + "\n"
