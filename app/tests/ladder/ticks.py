"""What the ladder readout reads off a played route: a skill's counted level, each card's running share, XP by source and
each saved mix's score, at any game instant, carried forward from the route's own saves (tests/ladder/readout.py). The
play is read, never decided on."""
from bisect import bisect_right, insort
from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Protocol
from functools import cache

from ashfall_app.engine import Rules, Save, flatten_shares
from ashfall_app.engine.cards import LaneState
from ashfall_app.engine.ids import ActionId, CardId, Runner, SkillId
from ashfall_app.engine.index import index
from ashfall_app.engine.mixes import MixLayer
from ashfall_app.engine.modifiers import FlowKind, RateRef
from ashfall_app.engine.phases import level_counted, phase_state, phase_top
from ashfall_app.engine.plan import mix_layer
from ashfall_app.engine.rates import line, running
from ashfall_app.engine.skills import level_for


class Timed(Protocol):
    @property
    def time(self) -> int: ...


def at_time[T: Timed](history: Sequence[T], run_on: Callable[[T, int], T]) -> Callable[[int], T]:
    """The save at instant t: `run_on` (the engine's advance, with nobody deciding) from the nearest save at or before
    t, whether one of `history` (ascending) or one an earlier call made. A bisection's probes then each run on only
    from the last one below them, so a search costs about one gap's events, not one per probe."""
    made: dict[int, T] = {s.time: s for s in history}
    times = sorted(made)

    def save_at(t: int) -> T:
        i = bisect_right(times, t) - 1
        assert i >= 0, f"the play has no save at or before {t}"
        if times[i] != t:
            made[t] = run_on(made[times[i]], t)
            insort(times, t)
        return made[t]
    return save_at


def counted(rules: Rules, save: Save, skill: SkillId) -> int:
    """The skill's level counted across phases (phases.level_counted): it never falls at a click. `save` is the instant."""
    st = next(s for s in save.skills if s.skill == skill)
    return level_counted(rules.curve, rules.prestige, st.phase.phase, st.xp.start_value)


def counted_at(rules: Rules, save_at: Callable[[int], Save], skill: SkillId) -> Callable[[int], int]:
    """`counted` as a function of the instant, remembering each instant it was asked (the bisection revisits some)."""
    @cache
    def at(t: int) -> int:
        return counted(rules, save_at(t), skill)
    return at


def phase_top_level(rules: Rules, save: Save, skill: SkillId) -> int:
    """The counted level at which the skill's current phase tops out; the curve's last level without prestige."""
    if rules.prestige is None:
        return level_for(rules.curve, rules.curve.thresholds[-1])
    return (phase_state(save, rules, skill).phase) * (rules.prestige.top_level - 1) + 1


def phase_progress(rules: Rules, save: Save, skill: SkillId) -> float:
    """Percent of the current phase's XP span the skill holds, 100 once it has topped out."""
    st = next(s for s in save.skills if s.skill == skill)
    if rules.prestige is None:
        return 100 * st.xp.start_value / rules.curve.thresholds[-1]
    n = st.phase.phase
    top, base = phase_top(rules.curve, rules.prestige, n), phase_top(rules.curve, rules.prestige, n - 1) if n > 1 else 0
    return min(100.0, 100 * (st.xp.start_value - base) / (top - base))


def card_shares(rules: Rules, save: Save) -> dict[str, int]:
    """Each card running at `save`'s instant with its effective share in basis points, standing actions left out."""
    cards = {str(c.id) for c in rules.cards}
    return {str(r): bp for r, bp in running(save, rules).shares.items() if str(r) in cards and bp > 0}


def _skill_of(rules: Rules, runner: Runner) -> SkillId | None:
    ix = index(rules)
    card = ix.cards.get(CardId(runner))
    return card.skill if card is not None else ix.standing[ActionId(runner)].skill


def xp_by_source(rules: Rules, save: Save) -> dict[str, dict[str, int]]:
    """XP per hour at `save`'s instant by skill, then by the card or standing action running it."""
    now = running(save, rules)
    out: dict[str, dict[str, int]] = {}
    for r, share in now.shares.items():
        skill = _skill_of(rules, r)
        if skill is not None:
            rate = line(save, rules, RateRef(r, FlowKind.XP), share, now.runs[r]).per_hour
            out.setdefault(str(skill), {})[str(r)] = rate
    return out


def level_width(rules: Rules, xp: int) -> int:
    """The XP between the start of the level `xp` stands in and the next (the last width past the curve's end)."""
    th = rules.curve.thresholds
    i = min(level_for(rules.curve, xp) - 1, len(th) - 1)
    return th[i] - (th[i - 1] if i > 0 else 0)


def mix_scores(rules: Rules, save: Save) -> dict[str, tuple[tuple[tuple[str, int], ...], float]]:
    """Each saved hands mix at `save`'s instant as the running one alone, with no order, tap or pause: its shape and
    the levels it gains per game hour (its cards' XP rates, each over the width of its skill's current level)."""
    alone = replace(save, orders=(), latches=(), pauses=(), lanes=tuple(LaneState(ls.lane) for ls in save.lanes))
    width = {st.skill: level_width(rules, st.xp.start_value) for st in save.skills}
    cards = {c.id: c for c in rules.cards}
    out: dict[str, tuple[tuple[tuple[str, int], ...], float]] = {}
    for m in save.mixes:
        if mix_layer(rules, save.mixes, m.id) is not MixLayer.HANDS:
            continue
        now = running(replace(alone, active=m.id), rules)
        score = 0.0
        for r, share in now.shares.items():
            card = cards.get(CardId(r))
            if card is not None and card.skill is not None:
                score += line(alone, rules, RateRef(r, FlowKind.XP), share, now.runs[r]).per_hour / width[card.skill]
        shape = tuple(sorted((str(c.card), c.share_bp) for c in flatten_shares(save.mixes, m.id)))
        out[str(m.id)] = (shape, score)
    return out
