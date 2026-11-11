"""Prestige in the content file: the rules numbers phases read and each skill's track of nodes (engine nodes.py), and
their conversion to the engine's types. A node may change a make, a card's work or a store's cap; the schema has no
way to aim one at XP, a cost or a lane's speed, so the load refuses such a node (engine nodechecks.py holds the rest,
a node acting on its own skill's work included)."""
from collections import Counter
from typing import Literal

from pydantic import Field

from ..engine import (
    ActionId, CardId, FlowKind, NodeDef, NodeId, NodeTarget, PrestigeDef, RateRef, Rules, SkillId, StoreCap, StoreId,
    WorkRef,
)
from ..engine.nodes import ORDINARY_ABSENCE_S
from ..engine.phases import span
from .entries import Entry


class PrestigeEntry(Entry):
    """[prestige] (engine PrestigeDef): the shown level a phase tops out at, the carry window in seconds, and how many
    unfinished nodes the menu offers."""

    top_level: int = Field(ge=2)
    carry_window_s: int = Field(ge=1)
    menu_size: Literal[2, 3]


class NodeChangeEntry(Entry):
    """What a node changes. target "make": `id` a card or standing action and `store` one it makes; "work": `id` a
    card; "cap": `id` a store."""

    target: Literal["make", "work", "cap"]
    id: str
    store: str | None = None


class NodeEntry(Entry):
    """One node of `skill`'s track (engine NodeDef): `ranks` clicks fill it, each changing its target by per_rank_bp
    more. A skill's track is its nodes in file order, the opening's first, then each chapter's."""

    id: str
    skill: str
    label_key: str
    changes: NodeChangeEntry
    ranks: int = Field(ge=1)
    per_rank_bp: int = Field(ge=1)


def prestige_def(p: PrestigeEntry | None) -> PrestigeDef | None:
    return None if p is None else PrestigeDef(p.top_level, p.carry_window_s, p.menu_size)


def node_def(n: NodeEntry, cards: set[str]) -> NodeDef:
    """The engine's node; `cards` the content's card ids, which tell a card from a standing action."""
    c = n.changes
    target: NodeTarget
    if c.target == "make":
        runner = CardId(c.id) if c.id in cards else ActionId(c.id)
        target = RateRef(runner, FlowKind.MAKE, None if c.store is None else StoreId(c.store))
    elif c.target == "work":
        target = WorkRef(CardId(c.id))
    else:
        target = StoreCap(StoreId(c.id))
    return NodeDef(NodeId(n.id), SkillId(n.skill), target, n.ranks, n.per_rank_bp)


def check_tracks(nodes: list[NodeEntry]) -> None:
    """ValueError naming a skill whose track is one node, or a node of more than one rank. With every node one rank and
    two or more nodes, every click but the last has two unfinished nodes to choose between whatever the pick order; a
    multi-rank node lets the other nodes fill first and leave a choiceless click."""
    held = Counter(n.skill for n in nodes)
    for skill, count in held.items():
        if count < 2:
            raise ValueError(f"prestige {skill}: its track is one node, so a click has no choice; a track holds at least two")
    for n in nodes:
        if n.ranks != 1:
            raise ValueError(f"prestige {n.skill}: node {n.id} has {n.ranks} ranks; a node is one rank, so no click but "
                             "the last is choiceless")


def check_phase_spans(rules: Rules) -> None:
    """ValueError unless, under rules with prestige, the carry window is at most the ordinary absence and every skill's
    phase takes at least that long at a full share of the runner (card or standing action) that trains it fastest:
    span / xp_per_hour >= ORDINARY_ABSENCE_S. Reads base XP rates; nothing may aim at XP or a lane's speed to raise
    them (engine nodechecks.py). Rules with no prestige pass."""
    if rules.prestige is None:
        return
    if rules.prestige.carry_window_s > ORDINARY_ABSENCE_S:
        raise ValueError(f"prestige: carry_window_s is longer than the ordinary absence ({ORDINARY_ABSENCE_S} s)")
    width = span(rules.curve, rules.prestige)
    for skill in rules.skills:
        fastest = max((r.xp_per_hour for r in (*rules.standing, *rules.cards) if r.skill == skill.id), default=0)
        if width < fastest * ORDINARY_ABSENCE_S:
            raise ValueError(f"skill {skill.id}: a full share of its fastest runner spans a phase inside an ordinary "
                             f"absence ({ORDINARY_ABSENCE_S} s)")
