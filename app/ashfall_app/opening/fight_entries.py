"""The content file's sides and threats (engine DESIGN.txt, "FIGHTS"), as Type Objects. Beside entries.py, whose
FightEntry names them."""
from pydantic import Field

from .entries import Entry


class SideEntry(Entry):
    """Who fights, by strength: `base` before any gear, skill pay or chip aimed at it (engine SideDef)."""

    id: str
    label_key: str
    base: int = Field(ge=0)


class ThreatEntry(Entry):
    """One entry of a roster: `base` before any trigger of the region's schedule raises it (engine ThreatDef)."""

    id: str
    label_key: str
    base: int = Field(ge=1)
