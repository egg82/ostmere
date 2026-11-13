"""A level is a thing, not only a number (docs/decisions.md): among the levels day one reaches, a skill goes at most
two levels in a row paying speed alone; at least every third brings something named. Reached levels are measured on a
played route (each skill's level as the player saw it when B3 is seen, day one's end); what a level pays is read off
the rules.

A level is named when something lands on it besides numbers: a find (a store gains items), an unlock or a start, a
line from a trigger that changes no number (a story moment), or a card's requires reading it (the builds, the crafts).
A trigger that only moves numbers (a work speed-up, a bigger batch, a cap) is not, with or without a line saying so.

Each leave point in day one names a level that pays something named, not only speed-ups: of the skill rows whose next
level the screen times at the leave (human_flags.leave), at least one is a named level."""
from dataclasses import dataclass

from ashfall_app.engine import Outcome, Rules, Save, view
from ashfall_app.engine.orders import AtLeast, SkillLevel
from tests.dayone.human_flags import Leave, leave
from tests.dayone.player import DayOnePlayer

MAX_RUN = 2
"""Levels in a row a skill may pay with numbers alone."""


def reached(p: DayOnePlayer) -> dict[str, int]:
    """Each skill's level in the last view the player saw by the time B3 was seen; none when B3 never was (reaches_b3
    owns that verdict)."""
    if "B3" not in p.seen_at:
        return {}
    stop = p.seen_at["B3"]
    levels: dict[str, int] = {}
    for save, v in p.history:
        if save.time > stop:
            break
        levels = {str(b.skill): b.level for b in v.skills}
    return levels


def _thing(o: Outcome) -> bool:
    return bool(o.stores or o.unlocks or o.starts or (o.lines and not o.modifiers and not o.raises))


def named(rules: Rules) -> dict[str, set[int]]:
    """Each skill's levels that pay something named."""
    out: dict[str, set[int]] = {}
    conds = [(t.when, _thing(t.outcome)) for t in rules.triggers] + [(r, True) for c in rules.cards for r in c.requires]
    for w, thing in conds:
        if thing and isinstance(w, AtLeast) and isinstance(w.subject, SkillLevel):
            out.setdefault(str(w.subject.skill), set()).add(w.value)
    return out


def runs(rules: Rules, top: dict[str, int]) -> list[str]:
    """Every stretch of more than MAX_RUN levels in a row, from level 2 to the skill's `top`, with nothing named."""
    paid = named(rules)
    found: list[str] = []
    for skill, last in sorted(top.items()):
        run: list[int] = []
        for level in range(2, last + 2):
            if level <= last and level not in paid.get(skill, set()):
                run.append(level)
                continue
            if len(run) > MAX_RUN:
                found.append(f"{skill} {run[0]}-{run[-1]}: {len(run)} levels with nothing named")
            run = []
    return found


@dataclass(frozen=True)
class LeavePoint:
    label: str
    levels: tuple[tuple[str, int], ...]
    """Each skill level the screen times at the leave (human_flags.leave), as (skill, level)."""


def leave_point(p: DayOnePlayer, label: str, exit_save: Save, shown: Leave) -> LeavePoint:
    now = {str(b.skill): b.level for b in view(exit_save, p.rules).skills}
    return LeavePoint(label, tuple((sk, now[sk] + 1) for kind, sk, _ in shown.payoffs if kind == "level"))


def day_one_exits(p: DayOnePlayer) -> list[tuple[str, Save]]:
    """Each leave point in day one: a visit's exit, up to B3 being seen (none when it never was)."""
    if "B3" not in p.seen_at:
        return []
    return [(f"V{v.index}", v.exit) for v in p.visits if v.exit is not None and v.exit.time <= p.seen_at["B3"]]


def leave_points(p: DayOnePlayer) -> list[LeavePoint]:
    """Day one's leave points with what their screens time (a forecast each: seconds of CPU on a route)."""
    return [leave_point(p, label, s, leave(p, s)) for label, s in day_one_exits(p)]


def speed_only_leaves(points: list[LeavePoint], rules: Rules) -> list[str]:
    """The leave points that time no level `rules` name something on: only speed-ups, or no level at all."""
    paid = named(rules)
    return [f"{pt.label}: names only {', '.join(f'{sk} {lv}' for sk, lv in pt.levels) or 'no level'}"
            for pt in points if not any(lv in paid.get(sk, set()) for sk, lv in pt.levels)]
