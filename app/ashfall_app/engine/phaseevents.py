"""The two instants a prestige phase brings, solved off the XP segment as a level-up is (DESIGN.txt, "PRESTIGE
PHASES"): TOP_OUT, where a skill's XP reaches its phase's top and its topped_at is set, and CARRY_END, where the carry
window closes and its XP stops. None under rules with no prestige."""
from dataclasses import replace

from .events import Event, EventKind
from .phases import carry_ends_at, phase_top
from .rebuild import rebuild
from .rules import Rules
from .segments import reach_time
from .state import PhaseState, Save, SkillState


def phase_events(save: Save, rules: Rules) -> list[Event]:
    """Each skill's TOP_OUT (topped_at None: when its XP reaches phase_top, now if it already has) and CARRY_END (its
    carry's end, while its XP still rises), in rules.skills order."""
    p = rules.prestige
    if p is None:
        return []
    found: list[Event] = []
    for i, st in enumerate(save.skills):
        if st.phase.topped_at is None:
            top = phase_top(rules.curve, p, st.phase.phase)
            t = save.time if st.xp.start_value >= top else reach_time(st.xp, top)
            if t is not None:
                found.append(Event(t, EventKind.TOP_OUT, i, st.skill))
        elif st.xp.rate > 0:
            end = carry_ends_at(p, st.phase)
            if end is not None:
                found.append(Event(max(end, save.time), EventKind.CARRY_END, i, st.skill))
    return found


def topped_out(save: Save, rules: Rules, i: int) -> Save:
    """TOP_OUT of the i-th skill: topped_at becomes save.time. Stale (the save as it is) once topped_at is set or
    while the XP is short of the top. No rate changes: the carry runs from here."""
    p, st = rules.prestige, save.skills[i]
    if p is None or st.phase.topped_at is not None or st.xp.start_value < phase_top(rules.curve, p, st.phase.phase):
        return save
    return _with_phase(save, i, replace(st.phase, topped_at=save.time))


def carry_ended(save: Save, rules: Rules, i: int) -> Save:
    """CARRY_END of the i-th skill: rebuilt, so its XP rate is 0 from now (phases.accrues). Stale before the carry's
    end or once the XP stands still."""
    p, st = rules.prestige, save.skills[i]
    end = None if p is None else carry_ends_at(p, st.phase)
    if end is None or save.time < end or st.xp.rate == 0:
        return save
    return rebuild(save, rules)


def _with_phase(save: Save, i: int, phase: PhaseState) -> Save:
    st = save.skills[i]
    return replace(save, skills=(*save.skills[:i], SkillState(st.skill, st.xp, phase), *save.skills[i + 1:]))
