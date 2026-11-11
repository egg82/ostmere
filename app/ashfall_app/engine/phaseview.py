"""A skill's row in the read model, read through its prestige phase (DESIGN.txt, "Read model", "PRESTIGE PHASES").
With rules.prestige None the row is the curve's, as before phases."""
from dataclasses import replace

from .gates import store_cap
from .ids import NodeId
from .nodes import NodeTarget
from .modifiers import StoreCap, WorkRef
from .phases import at_top, level_counted, level_shown, next_level_xp, span, waiting_levels
from .pickentries import nodes_by_id
from .prestige import mastered, menu, pick_owed, ranks_taken, undo_open
from .rates import FULL, line, work_line
from .rules import Rules
from .segments import reach_time
from .skills import xp_for
from .state import Save, SkillState
from .units import BP
from .viewparts import MenuNode, SkillBar, SkillPhase


def skill_bar(save: Save, rules: Rules, st: SkillState) -> SkillBar:
    """The skill's row at save.time: its shown level, the bar's ends within the phase, and its SkillPhase."""
    p, phase, xp = rules.prestige, st.phase.phase, st.xp.start_value
    level = level_shown(rules.curve, p, phase, xp)
    base = 0 if p is None else (phase - 1) * span(rules.curve, p)
    nxt = next_level_xp(rules.curve, p, phase, xp)
    return SkillBar(st.skill, st.xp, level, base + xp_for(rules.curve, level), nxt,
                    None if nxt is None else reach_time(st.xp, nxt), _phase(save, rules, st))


def _phase(save: Save, rules: Rules, st: SkillState) -> SkillPhase | None:
    p = rules.prestige
    if p is None:
        return None
    phase, xp = st.phase.phase, st.xp.start_value
    return SkillPhase(
        phase, level_counted(rules.curve, p, phase, xp), at_top(save, rules, st.skill),
        waiting_levels(rules.curve, p, phase, xp), tuple(_menu_node(save, rules, n) for n in menu(save, rules, st.skill)),
        undo_open(save, rules, st.skill), mastered(save, rules, st.skill), pick_owed(st.phase), st.phase.topped_at,
        st.phase.picks, st.phase.parked)


def _menu_node(save: Save, rules: Rules, node: NodeId) -> MenuNode:
    d = nodes_by_id(rules)[node]
    picked = tuple(replace(k, phase=replace(k.phase, picks=(*k.phase.picks, node))) if k.skill == d.skill else k
                   for k in save.skills)
    return MenuNode(node, ranks_taken(save, rules, node), d.ranks, _target_value(save, rules, d.target),
                    _target_value(replace(save, skills=picked), rules, d.target))


def _target_value(save: Save, rules: Rules, target: NodeTarget) -> int:
    """The target as `save`'s stack makes it, at a full share and a FULL run."""
    if isinstance(target, StoreCap):
        return store_cap(save, rules, target.store)
    if isinstance(target, WorkRef):
        return work_line(save, rules, target.card, BP, FULL).per_hour
    return line(save, rules, target, BP, FULL).per_hour
