"""A skill's prestige phase: its state and the XP rules phases read (DESIGN.txt, "PRESTIGE PHASES").

XP climbs on one segment across every phase. Phase n's top is n spans of the curve up to rules.prestige.top_level
(phase_top). At its top the skill's shown level stops and waits for the player's click (prestige.Prestige); XP keeps
accruing for the carry window, then stops, and never passes the next phase's top (xp_ceiling, accrues). The click
lifts the top by one span and the shown level counts from 1 again, read off the carried XP (level_shown).

Every function here is pure. With rules.prestige None, each reads as the engine reads XP without prestige: the cap is
the curve's last threshold and the level is level_for(curve, xp).
"""
from .ids import SkillId
from .nodes import PrestigeDef
from .rules import PacingCurve, Rules
from .segments import value_at
from .skills import level_for, xp_for
from .state import PhaseState, Save, SkillState


def span(curve: PacingCurve, prestige: PrestigeDef) -> int:
    """XP one phase spans: xp_for(curve, prestige.top_level), > 0."""
    return xp_for(curve, prestige.top_level)


def phase_top(curve: PacingCurve, prestige: PrestigeDef, phase: int) -> int:
    """The total XP at which `phase` tops out: phase * span(curve, prestige). ValueError for phase < 1."""
    if phase < 1:
        raise ValueError(f"phase {phase} is below 1")
    return phase * span(curve, prestige)


def xp_ceiling(curve: PacingCurve, prestige: PrestigeDef | None, phase: int) -> int:
    """The most total XP a skill in `phase` can hold, its XP segment's limit: one unit short of the next phase's top,
    phase_top(phase + 1) - 1, so a click always lands below the new phase's top and one absence never leaves more
    than one click waiting. With prestige None, the curve's last threshold. ValueError for phase < 1."""
    if phase < 1:
        raise ValueError(f"phase {phase} is below 1")
    return curve.thresholds[-1] if prestige is None else phase_top(curve, prestige, phase + 1) - 1


def carry_ends_at(prestige: PrestigeDef, state: PhaseState) -> int | None:
    """The instant XP stops accruing in this phase: state.topped_at + prestige.carry_window_s; None while
    state.topped_at is None."""
    return None if state.topped_at is None else state.topped_at + prestige.carry_window_s


def accrues(prestige: PrestigeDef | None, state: PhaseState, t: int) -> bool:
    """Whether the skill's XP rate runs at instant t: False exactly when prestige is set and t >= carry_ends_at. So
    accrual stops at the earlier of the carry's end (a time) and xp_ceiling (a value, the segment's limit); while it
    has stopped the skill's XP rate is 0 and its runners' other lines run unchanged. With prestige None, always True."""
    if prestige is None:
        return True
    end = carry_ends_at(prestige, state)
    return end is None or t < end


def level_shown(curve: PacingCurve, prestige: PrestigeDef | None, phase: int, xp: int) -> int:
    """The level the skill's row shows: level_for(curve, min(xp, phase_top(phase)) - phase_top(phase - 1)), with
    phase_top(0) = 0. In 1..prestige.top_level; top_level exactly when xp >= phase_top(phase). Monotone in xp within a
    phase. With prestige None, level_for(curve, xp). Defined for xp >= phase_top(phase - 1), which every save holds."""
    if prestige is None:
        return level_for(curve, xp)
    width = span(curve, prestige)
    return level_for(curve, min(xp, phase * width) - (phase - 1) * width)


def level_counted(curve: PacingCurve, prestige: PrestigeDef | None, phase: int, xp: int) -> int:
    """The level a SkillLevel condition reads: levels counted across phases,
    (phase - 1) * (prestige.top_level - 1) + level_shown(curve, prestige, phase, xp). It never falls at a click (a
    skill at its top in phase n counts as much as level 1 of phase n + 1), so a trigger or latch already true stays
    true. With prestige None, level_for(curve, xp)."""
    if prestige is None:
        return level_for(curve, xp)
    return (phase - 1) * (prestige.top_level - 1) + level_shown(curve, prestige, phase, xp)


def waiting_levels(curve: PacingCurve, prestige: PrestigeDef, phase: int, xp: int) -> int:
    """Levels the carried XP would land at a click now: level_shown(curve, prestige, phase + 1, xp) - 1 when xp >=
    phase_top(phase), else 0. What the row shows as "+N levels waiting" and the prestige sheet as the level the new
    phase starts at (that plus 1)."""
    if xp < phase_top(curve, prestige, phase):
        return 0
    return level_shown(curve, prestige, phase + 1, xp) - 1


def phase_state(save: Save, rules: Rules, skill: SkillId) -> PhaseState:
    """The skill's PhaseState in `save` (FIRST_PHASE for a skill that has never topped out). KeyError for a skill not
    in the save."""
    return skill_state(save, skill).phase


def at_top(save: Save, rules: Rules, skill: SkillId) -> bool:
    """The skill waits for a click: rules.prestige is set and its XP at save.time is at least
    phase_top(its phase); equivalently its PhaseState.topped_at is not None. False with rules.prestige None."""
    if rules.prestige is None:
        return False
    st = skill_state(save, skill)
    return value_at(st.xp, save.time) >= phase_top(rules.curve, rules.prestige, st.phase.phase)


def skill_state(save: Save, skill: SkillId) -> SkillState:
    """The skill's SkillState in `save`. KeyError for a skill not in the save."""
    for st in save.skills:
        if st.skill == skill:
            return st
    raise KeyError(skill)


def next_level_xp(curve: PacingCurve, prestige: PrestigeDef | None, phase: int, xp: int) -> int | None:
    """The total XP at which the shown level next rises, where a LEVEL_UP falls: the curve's next threshold above
    `xp`, read from the phase's start, up to the phase's top; None at the top (the levels the carry passes wait for
    the click) or, with prestige None, past the curve's last threshold."""
    if prestige is None:
        return next((th for th in curve.thresholds if th > xp), None)
    base, top = (phase - 1) * span(curve, prestige), phase_top(curve, prestige, phase)
    return next((x for th in curve.thresholds if xp < (x := base + th) <= top), None)


def counted_xp(curve: PacingCurve, prestige: PrestigeDef | None, phase: int, level: int) -> int | None:
    """The least total XP in `phase` at which level_counted reaches `level` (>= 1): what a SkillLevel condition's rise
    is solved against. None when no XP in the phase reaches it: past its top, which only a click lifts, or, with
    prestige None, past the curve's last level."""
    if prestige is None:
        return None if level > len(curve.thresholds) + 1 else xp_for(curve, level)
    shown = level - (phase - 1) * (prestige.top_level - 1)
    if shown > prestige.top_level:
        return None
    return (phase - 1) * span(curve, prestige) + xp_for(curve, max(shown, 1))
