"""What day two's routes say about the next stretch: when B5's and B6's placeholder levels come (beats.yaml: each gated
on a day-three step, A20 or A21, beside a skill level and the beat before), and the Camp's levels 7 and 8.

A20 and A21 have no content yet, so their simulator side is only this: each beat lands at the later of its step, its
level and the beat before. Nothing past B4 is content, so a level's time is projected from the save at B4 at the XP
rate the hands averaged over day two (B3 to B4), not played; `projected_check` plays one route on with nobody deciding
to show how far the projection is off. A beat's level lands "inside day three" when it comes after B4 and no later
than B4 plus DAY_TWO_H, the length day two was written to take: earlier, the level gates nothing
(the step alone does); later, the level holds the beat past the chapter."""
from dataclasses import dataclass

from ashfall_app.engine import Save, advance
from ashfall_app.engine.skills import level_for, xp_for
from ashfall_app.opening.convert import camp_trigger_id
from tests.daytwo.checks import b3_at
from tests.daytwo.player import DayTwoPlayer

PLACEHOLDERS = {"B5": ("foraging", 10), "B6": ("scavenging", 20)}
"""beats.yaml's day-three level gates (Open 1's placeholders)."""
CAMP_LEVELS = (7, 8)
DAY_TWO_H = 30.0
"""Day two's written length in game hours after B3 (content/team/day-two.md, "Landing targets"): where the report reads
a projected level as inside day three or past it."""


@dataclass(frozen=True)
class LevelAt:
    beat: str
    skill: str
    level: int
    at_b3: int
    at_b4: int
    hours_after_b4: float | None
    """None: the hands train no XP in it (never)."""

    @property
    def verdict(self) -> str:
        h = self.hours_after_b4
        if h is None:
            return "never (no XP in it)"
        if h <= 0:
            return "already reached by B4: the level gates nothing"
        return "inside day three" if h <= DAY_TWO_H else "past day three"


def xp(save: Save, skill: str) -> int:
    seg = next(s.xp for s in save.skills if s.skill == skill)
    value = seg.start_value + seg.rate * (save.time - seg.start)
    return value if seg.limit is None else min(value, seg.limit) if seg.rate >= 0 else max(value, seg.limit)


def save_at(p: DayTwoPlayer, t: int) -> Save:
    return next(s for s, _ in p.history if s.time >= t)


def level_at(p: DayTwoPlayer, beat: str) -> LevelAt:
    skill, level = PLACEHOLDERS[beat]
    a, b = save_at(p, b3_at(p)), save_at(p, p.landed_at["B4"])
    xa, xb = xp(a, skill), xp(b, skill)
    curve = p.rules.curve
    need = xp_for(curve, level) - xb
    rate = (xb - xa) / max(1, b.time - a.time)
    hours = 0.0 if need <= 0 else (round(need / rate / 3600, 1) if rate > 0 else None)
    return LevelAt(beat, skill, level, level_for(curve, xa), level_for(curve, xb), hours)


def level_after(p: DayTwoPlayer, skill: str, hours: float) -> int:
    """The skill's projected level `hours` after B4, at day two's average XP rate."""
    a, b = save_at(p, b3_at(p)), save_at(p, p.landed_at["B4"])
    rate = (xp(b, skill) - xp(a, skill)) / max(1, b.time - a.time)
    return level_for(p.rules.curve, round(xp(b, skill) + max(0.0, rate) * hours * 3600))


def projected_check(p: DayTwoPlayer, hours: float) -> dict[str, int]:
    """Each placeholder skill's level after `hours` more of nobody deciding from the save at B4 (played, not projected)."""
    b = save_at(p, p.landed_at["B4"])
    later = advance(b, p.rules, b.time + round(hours * 3600))
    return {s: level_for(p.rules.curve, xp(later, s)) for s, _ in PLACEHOLDERS.values()}


def camp(p: DayTwoPlayer) -> dict[int, float | None]:
    """Camp levels 7 and 8: game hours after B3 each landed, None if not on this play."""
    fired: dict[int, float | None] = {}
    for n in CAMP_LEVELS:
        tid = camp_trigger_id(n)
        i = next((i for i, t in enumerate(p.rules.triggers) if t.id == tid), None)
        at = None if i is None else next((s.time for s, _ in p.history if s.fired[i]), None)
        fired[n] = None if at is None else round((at - b3_at(p)) / 3600, 2)
    return fired
