"""A skill's levels and prestige nodes on the wire (CONTRACT.txt; re-exported from content_models.py)."""
from enum import StrEnum

from pydantic import BaseModel


class LevelPays(BaseModel):
    """What a level brings, shown before it lands: words (pays_key), "?" for a story unlock."""

    level: int
    pays_key: str
    change_bp: list[int]
    """The level's modifiers as signed changes in basis points (+1000 is +10%), each distinct value once, in the order
    authored; the {pct} and {pct_b} slots of pays_key. Empty for a level that pays a find."""
    speeds: list[str]
    """The cards the level makes faster, in card order: a work entry's card, every card on a lane entry's lane. Empty
    when it changes no card's speed (a rate, a cap, a find)."""


class NodeTarget(StrEnum):
    MAKE = "make"
    WORK = "work"
    CAP = "cap"


class NodeChange(BaseModel):
    """What a node's ranks change, as the content authors it: `make`, what runner `id` (a card or standing action)
    makes of `store`; `work`, card `id`'s work speed; `cap`, store `id`'s cap. The page names it by those ids' labels."""

    target: NodeTarget
    id: str
    store: str | None


class NodeInfo(BaseModel):
    """One node of `skill`'s prestige track (CONTRACT.txt, "PRESTIGE PHASES"); SkillPrestige.menu_nodes names it."""

    node: str
    skill: str
    label_key: str
    change: NodeChange


class SkillInfo(BaseModel):
    skill: str
    label_key: str
    levels: list[LevelPays]
    """The levels that bring something, in order: the row shows the first above its level."""
