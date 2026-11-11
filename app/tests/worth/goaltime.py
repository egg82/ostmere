"""The open goals on a save and how fast a mix moves each (docs/design/worth-a-change.md, "What the simulator
measures"). A goal is a skill's next level, for a skill on screen, below its phase's top, with a hands card in view that
trains it and could run now; every level carries a marker, so the next level is the next marker (tests/dayone/goals.py).
A card's cap is not a goal here: a capped card is a tap, not a mix.

A mix's XP rate into a skill is the engine's own rate formula (engine/modifiers.py: base, modifiers, share) summed over
the mix's ready cards that train it, a card that could not run now giving its share to the rest of its mix as SPENT
does (engine DESIGN.txt, "SPENT"). It is read at the visit's instant, so it leaves out what an order or a tap takes
from the mix later and an input running dry; the readout prints how far the kept mix's rates came true over each absence."""
from dataclasses import dataclass

from ashfall_app.engine import BP, HANDS, CardId, FlowKind, RateRef, Rules, Save, SkillId, View, explain, flatten_shares
from ashfall_app.engine.phases import at_top, next_level_xp
from ashfall_app.engine.segments import value_at

Shares = tuple[tuple[str, int], ...]
"""A mix as (card, share_bp) pairs, sorted by card, so equal mixes compare equal."""


@dataclass(frozen=True)
class Goal:
    skill: str
    level: int
    top: bool
    """The next level is the phase's top."""
    xp_left: int
    card: str
    """The ready hands card that trains the skill fastest at a full share."""
    alone_s: float
    """Seconds `card` at a full share takes to land the goal."""

    @property
    def label(self) -> str:
        return f"{self.skill} {'top' if self.top else ''}{self.level}"


@dataclass(frozen=True)
class Board:
    """What a visit's setups are scored against: its open goals and each ready skill card's skill and full rate."""
    goals: tuple[Goal, ...]
    cards: dict[str, tuple[str, int]]
    """Ready hands card: (its skill, its full_rate)."""
    stuck: frozenset[str]
    """Cards in view that could not run now: in a mix, their shares yield to the rest of it."""


def full_rate(save: Save, rules: Rules, card: str) -> int:
    """The card's XP rate at a full share, modifiers applied (XP per second in quantity units: engine/units.py)."""
    ex = explain(save, rules, RateRef(CardId(card), FlowKind.XP, None))
    rate = ex.base_per_hour * max(0, BP + sum(m.amount_bp for m in ex.adds)) // BP
    for m in ex.muls:
        rate = rate * m.amount_bp // BP
    return rate


def ready_cards(save: Save, rules: Rules, v: View) -> dict[str, tuple[str, int]]:
    """Each uncapped hands card in view that trains a skill and could run now (inputs on hand, nothing required unmet)."""
    ready = {c.card for c in v.cards if c.blocker is None}
    out: dict[str, tuple[str, int]] = {}
    for c in rules.cards:
        if c.lane == HANDS and c.skill is not None and c.cap is None and str(c.id) in ready:
            rate = full_rate(save, rules, str(c.id))
            if rate > 0:
                out[str(c.id)] = (str(c.skill), rate)
    return out


def board(save: Save, v: View, rules: Rules) -> Board:
    cards = ready_cards(save, rules, v)
    best: dict[str, tuple[str, int]] = {}
    for card, (skill, rate) in cards.items():
        if skill not in best or rate > best[skill][1]:
            best[skill] = (card, rate)
    top = None if rules.prestige is None else rules.prestige.top_level
    goals: list[Goal] = []
    for bar in v.skills:
        found = best.get(bar.skill)
        now, target = xp(save, rules, bar.skill)
        if found is not None and target is not None and not at_top(save, rules, SkillId(bar.skill)):
            card, rate = found
            goals.append(Goal(bar.skill, bar.level + 1, bar.level + 1 == top, target - now, card,
                              (target - now) / rate))
    return Board(tuple(goals), cards, frozenset(c.card for c in v.cards if c.blocker is not None))


def xp(save: Save, rules: Rules, skill: str) -> tuple[int, int | None]:
    """The skill's XP at the save's instant and the XP its next shown level rises at (None at its phase's top)."""
    st = next(k for k in save.skills if k.skill == SkillId(skill))
    x = value_at(st.xp, save.time)
    return x, next_level_xp(rules.curve, rules.prestige, st.phase.phase, x)


def own_mix(save: Save) -> Shares:
    """The player's own mix, flattened; empty when none is active."""
    if save.active is None:
        return ()
    return tuple(sorted((str(c.card), c.share_bp) for c in flatten_shares(save.mixes, save.active)))


def rates(b: Board, shares: Shares) -> dict[str, float]:
    """XP per second into each skill with `shares` running: the cards that can run at their shares, raised in proportion
    by the shares of those that could not."""
    stuck = sum(bp for c, bp in shares if c in b.stuck)
    running = sum(bp for c, bp in shares if c not in b.stuck)
    lift = (running + stuck) / running if running else 0.0
    out: dict[str, float] = {}
    for c, bp in shares:
        if c in b.cards:
            skill, rate = b.cards[c]
            out[skill] = out.get(skill, 0.0) + rate * bp / BP * lift
    return out

