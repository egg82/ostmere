"""Wire models of a prestige node (contract/prestige-phases.txt, "PRESTIGE PHASES"); the conventions in models.py hold here."""
from enum import StrEnum

from pydantic import BaseModel


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
    """One node of `skill`'s prestige track (contract/prestige-phases.txt, "PRESTIGE PHASES"); SkillPrestige.menu_nodes names it."""

    node: str
    skill: str
    label_key: str
    change: NodeChange
