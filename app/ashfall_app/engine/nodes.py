"""Prestige as data: a skill's track of nodes and the rules numbers phases read (Type Object; DESIGN.txt, "PRESTIGE
PHASES"). Content, never state: a save holds only which nodes it picked (phases.PhaseState)."""
from dataclasses import dataclass

from .ids import NodeId, SkillId
from .modifiers import RateRef, StoreCap, WorkRef

ORDINARY_ABSENCE_S = 48 * 3600
"""The ordinary absence, in seconds: a carry window is never longer, and no skill's phase is spanned faster at a full
share of its quickest runner (the loader's check, opening/prestige.py), so the carry window binds before the XP
ceiling does and no whole phase falls inside one absence."""

NODE_PREFIX = "node:"
"""Every rank entry's source starts with it, followed by its node's id (pickentries.pick_source)."""

type NodeTarget = RateRef | WorkRef | StoreCap
"""What a node may change: a card's or standing action's make (a RateRef of kind MAKE), a card's work speed, or a
store's cap. Never XP, a cost, a lane's speed or a strength (nodechecks.check_nodes)."""


@dataclass(frozen=True)
class NodeDef:
    """One node of `skill`'s track. Each click of that skill puts one rank into one node; a node with every rank taken
    is finished and leaves the menu.

    target: what it changes (NodeTarget), always outside its own skill: a RateRef's runner and a WorkRef's card never
    train `skill`. ranks >= 1: how many clicks can go into it. per_rank_bp >= 1: what one rank adds, in basis points;
    ranks within a node add, so n ranks change the target by BP + n * per_rank_bp as one MUL_BP entry, and separate
    nodes compound (pickentries.pick_entries). A full track's bound is therefore the product of
    (BP + ranks * per_rank_bp) / BP over its nodes, fixed when the content is written.

    A skill's track is its nodes in rules.nodes order; that order is the menu's (prestige.menu)."""

    id: NodeId
    skill: SkillId
    target: NodeTarget
    ranks: int
    per_rank_bp: int


@dataclass(frozen=True)
class PrestigeDef:
    """The rules numbers every skill's phases read. Rules.prestige None: these rules have no prestige, XP is capped
    at the curve's last threshold as before, and Prestige and UndoPick are refused (PrestigeRefusal.NO_PRESTIGE).

    top_level: the shown level at which a phase tops out; 2 <= top_level <= len(curve.thresholds) + 1. Every phase
    reads the same curve from level 1, so each phase spans xp_for(curve, top_level) XP (phases.phase_top).
    carry_window_s >= 1: seconds after topping out that XP keeps accruing (phases.carry_ends_at).
    menu_size, 2 or 3: how many unfinished nodes the menu offers at most (prestige.menu)."""

    top_level: int
    carry_window_s: int
    menu_size: int
