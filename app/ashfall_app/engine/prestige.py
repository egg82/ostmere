"""Applying the prestige verbs, and the reads the prestige sheet needs (DESIGN.txt, "PRESTIGE PHASES"). The verbs and
their refusals: prestigeverbs.py."""
from dataclasses import replace

from .ids import NodeId, SkillId
from .index import derived, index
from .nodes import NodeDef, PrestigeDef
from .phases import at_top, level_shown, phase_top, skill_state
from .pickentries import held, nodes_by_id, ranks
from .prestigeverbs import MovePick, Prestige, PrestigeRefusal, PrestigeRefused, UndoPick
from .rebuild import rebuild
from .rules import PacingCurve, Rules
from .segments import value_at
from .state import ParkedRank, PhaseState, Save
from .unlocked import is_unlocked
from .unlocks import Unlock, UnlockKind


def track(rules: Rules, skill: SkillId) -> tuple[NodeDef, ...]:
    """`skill`'s nodes, in rules.nodes order; empty for a skill with none or rules with no prestige."""
    tracks = derived(rules, "_tracks", _tracks)
    return tracks.get(skill, ())


def _tracks(rules: Rules) -> dict[SkillId, tuple[NodeDef, ...]]:
    found: dict[SkillId, list[NodeDef]] = {}
    for n in rules.nodes:
        found.setdefault(n.skill, []).append(n)
    return {s: tuple(ns) for s, ns in found.items()}


def ranks_taken(save: Save, rules: Rules, node: NodeId) -> int:
    """How many of the node's skill's picks name `node`, 0..NodeDef.ranks; 0 for an unknown node."""
    found = nodes_by_id(rules).get(node)
    return 0 if found is None else ranks(save, found)


def menu(save: Save, rules: Rules, skill: SkillId) -> tuple[NodeId, ...]:
    """The nodes the skill's next pick may go into: the first rules.prestige.menu_size nodes of its track, in track
    order, with ranks_taken below NodeDef.ranks. No draw: it is a function of the track and the picks alone, so it is
    fixed for the whole phase (picks change only at a click, an undo or a move; a parked rank holds its node as a taken one does) and the player sees the coming choice all
    phase. After an UndoPick it is the menu the undone pick came from. Empty with rules.prestige None, an unknown
    skill, or every node finished. Read only."""
    if rules.prestige is None:
        return ()
    open_nodes = [n.id for n in track(rules, skill) if held(save, n) < n.ranks]
    return tuple(open_nodes[:rules.prestige.menu_size])


def mastered(save: Save, rules: Rules, skill: SkillId) -> bool:
    """The skill's track is done: rules.prestige is set, no pick is owed and the menu is empty, so every click is
    refused TRACK_DONE and the skill rests at its top for good. True from the start for a skill with no nodes. False
    with rules.prestige None or an unknown skill."""
    if rules.prestige is None or skill not in index(rules).skill_pos:
        return False
    return not pick_owed(skill_state(save, skill).phase) and not menu(save, rules, skill)


def undo_open(save: Save, rules: Rules, skill: SkillId) -> bool:
    """UndoPick of the skill would act now: its phase is above 1, no pick is owed, and its shown level
    (phases.level_shown) is still its PhaseState.click_level."""
    if rules.prestige is None or skill not in index(rules).skill_pos:
        return False
    st = skill_state(save, skill)
    ps = st.phase
    if ps.phase <= 1 or pick_owed(ps):
        return False
    return level_shown(rules.curve, rules.prestige, ps.phase, value_at(st.xp, save.time)) == ps.click_level


def refusal(save: Save, rules: Rules, verb: Prestige | UndoPick | MovePick) -> PrestigeRefusal | None:
    """Why the player's `verb` cannot act on `save` now, the first that applies in the order each verb's docstring
    gives; None when it can. Read only."""
    if rules.prestige is None:
        return PrestigeRefusal.NO_PRESTIGE
    if verb.skill not in index(rules).skill_pos:
        return PrestigeRefusal.UNKNOWN_SKILL
    if not is_unlocked(save, rules, Unlock(UnlockKind.SKILL, verb.skill)):
        return PrestigeRefusal.LOCKED_SKILL
    ps = skill_state(save, verb.skill).phase
    if isinstance(verb, MovePick):
        return _move_refusal(save, rules, verb, ps)
    if isinstance(verb, UndoPick):
        if ps.phase <= 1 or pick_owed(ps) or not ps.picks:
            return PrestigeRefusal.NOTHING_TO_UNDO
        return None if undo_open(save, rules, verb.skill) else PrestigeRefusal.UNDO_CLOSED
    offered = menu(save, rules, verb.skill)
    if not pick_owed(ps):
        if not at_top(save, rules, verb.skill):
            return PrestigeRefusal.NOT_AT_TOP
        if not offered:
            return PrestigeRefusal.TRACK_DONE
    return None if verb.node in offered else PrestigeRefusal.NOT_ON_MENU


def _move_refusal(save: Save, rules: Rules, verb: MovePick, ps: PhaseState) -> PrestigeRefusal | None:
    if pick_owed(ps):
        return PrestigeRefusal.PICK_OWED
    if verb.node not in ps.picks:
        return PrestigeRefusal.NOT_PICKED
    on_menu = verb.to != verb.node and verb.to in menu(save, rules, verb.skill)
    return None if on_menu else PrestigeRefusal.NOT_ON_MENU


def applied(save: Save, rules: Rules, verb: Prestige | UndoPick | MovePick) -> Save:
    """The save after the player's `verb` at save.time, as each verb's docstring says, its rates rebuilt (a rank
    changes its target's stack). PrestigeRefused(refusal(...)) when it cannot act, the save unchanged."""
    why = refusal(save, rules, verb)
    if why is not None:
        raise PrestigeRefused(why)
    st = skill_state(save, verb.skill)
    ps = st.phase
    if isinstance(verb, UndoPick):
        after = replace(ps, picks=ps.picks[:-1])
    elif isinstance(verb, MovePick):
        i = ps.picks.index(verb.node)
        after = replace(ps, picks=(*ps.picks[:i], *ps.picks[i + 1:]),
                        parked=(*ps.parked, ParkedRank(verb.to, ps.phase + 2)))
    elif pick_owed(ps):
        after = replace(ps, picks=(*ps.picks, verb.node))
    elif rules.prestige is not None:
        after = _clicked(save.time, rules.curve, rules.prestige, value_at(st.xp, save.time), ps, verb.node)
    else:
        raise PrestigeRefused(PrestigeRefusal.NO_PRESTIGE)
    skills = tuple(replace(k, phase=after) if k.skill == verb.skill else k for k in save.skills)
    return rebuild(replace(save, skills=skills), rules)


def _clicked(t: int, curve: PacingCurve, prestige: PrestigeDef, xp: int, ps: PhaseState, node: NodeId) -> PhaseState:
    """The click at t: one phase up, the parked ranks now due settled and the rank appended after them, the level the
    held XP shows in the new phase, and topped_at t if that XP already reaches the new phase's top."""
    phase = ps.phase + 1
    topped = t if xp >= phase_top(curve, prestige, phase) else None
    settled = tuple(p.node for p in ps.parked if p.due <= phase)
    waiting = tuple(p for p in ps.parked if p.due > phase)
    return PhaseState(phase, (*ps.picks, *settled, node), topped, level_shown(curve, prestige, phase, xp), waiting)


def pick_owed(ps: PhaseState) -> bool:
    """UndoPick took the phase's pick back and the next Prestige fills it (from the same menu, at or below the top)."""
    return len(ps.picks) + len(ps.parked) == ps.phase - 2
