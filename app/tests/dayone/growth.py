"""Time to each next level, per skill, under a fixed mix: the loop between what a level pays and how fast the next one
comes must stay tame. In Pecorella's terms ("The Math of Idle Games", parts I-III, Kongregate, 2016), a level costing
c times the last while paying s times the speed takes c / s times as long; c < s compounds into a runaway. Here a
level's speed-up goes to its card's work (more made per hour, engine WorkRef), which no XP line reads, so only what
aims at XP itself (a RateRef on XP, a lane's speed) shortens a level. Read off the rules: the curve's steps and the XP
modifiers the skill's own levels land, card by card.

Each skill's climb is read the same way and reported (tests/opening/report.py), never held to a band: the hours a full
share of its fastest runner takes to climb the curve."""
from math import prod

from ashfall_app.engine import FlowKind, LaneSpeed, ModifierKind, RateRef, Rules
from ashfall_app.engine.orders import AtLeast, SkillLevel
from ashfall_app.engine.units import BP, SECONDS_PER_HOUR

RELEASED_DIPS = frozenset({3})
"""Levels whose step is shorter than the one before on the shipped curve (6 items of XP to level 2, then 4 to 3).
Released thresholds never change (the release lock), so this one is held; the set never grows."""


def steps(rules: Rules) -> list[int]:
    """XP from each level to the next: steps[0] is level 1 to 2."""
    th = rules.curve.thresholds
    return [b - a for a, b in zip((0, *th), th)]


def xp_factor(rules: Rules, skill: str, card: str, lane: str, level: int) -> float:
    """The card's XP rate at `level` over its base: XP and lane-speed entries the skill's levels up to `level` land."""
    muls: list[int] = []
    adds: list[int] = []
    for t in rules.triggers:
        w = t.when
        if not (isinstance(w, AtLeast) and isinstance(w.subject, SkillLevel) and w.subject.skill == skill
                and w.value <= level):
            continue
        for m in t.outcome.modifiers:
            aimed = (isinstance(m.target, RateRef) and m.target.runner == card and m.target.kind is FlowKind.XP) \
                or (isinstance(m.target, LaneSpeed) and m.target.lane == lane)
            if aimed:
                (muls if m.kind is ModifierKind.MUL_BP else adds).append(m.amount_bp)
    return max(0, BP + sum(adds)) / BP * prod(x / BP for x in muls)


def level_times(rules: Rules, skill: str) -> dict[str, list[float]]:
    """Per card training `skill`: hours from level n to n+1 at a full share, n = 1, 2, ..."""
    out: dict[str, list[float]] = {}
    for c in rules.cards:
        if c.skill != skill or c.xp_per_hour <= 0:
            continue
        rate = c.xp_per_hour
        out[str(c.id)] = [step / (rate * xp_factor(rules, skill, str(c.id), str(c.lane), n)) / SECONDS_PER_HOUR
                          for n, step in enumerate(steps(rules), start=1)]
    return out


def runaway(rules: Rules) -> list[str]:
    """Every level reached sooner than the one before it, under the same card at a full share, off the held dips."""
    found: list[str] = []
    skills = {str(c.skill) for c in rules.cards if c.skill is not None}
    for skill in sorted(skills):
        for card, times in level_times(rules, skill).items():
            for n, (a, b) in enumerate(zip(times, times[1:]), start=2):
                if b < a and n + 1 not in RELEASED_DIPS:
                    found.append(f"{skill} by {card}: level {n + 1} comes in {b:.3g} h after {a:.3g} h for level {n}")
    return found


def fastest_rates(rules: Rules) -> dict[str, int]:
    """Each skill with a runner (card or standing action) that trains it: that runner's base XP rate, the fastest."""
    out: dict[str, int] = {}
    for r in (*rules.standing, *rules.cards):
        if r.skill is not None and r.xp_per_hour > 0:
            out[str(r.skill)] = max(out.get(str(r.skill), 0), r.xp_per_hour)
    return out


def climb_hours(rules: Rules) -> dict[str, float]:
    """Each skill's hours to the curve's top at a full share of its fastest runner."""
    top = rules.curve.thresholds[-1]
    return {skill: top / rate / SECONDS_PER_HOUR for skill, rate in sorted(fastest_rates(rules).items())}
