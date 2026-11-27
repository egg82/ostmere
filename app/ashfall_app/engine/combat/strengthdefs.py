"""The kinds a fight's strengths are read for: who fights and what they fight (design/fights.txt, "FIGHTS")."""
from dataclasses import dataclass

from ..core.ids import SideId, ThreatId


@dataclass(frozen=True)
class SideDef:
    """A Type Object for one side, by strength: base >= 0 before any entry aimed at its SideStrength."""

    id: SideId
    base: int


@dataclass(frozen=True)
class ThreatDef:
    """A Type Object for one entry of a roster: base > 0 before any entry aimed at its ThreatStrength. members (>= 1):
    2 or more marks a group, fought one after another, whose due members a chain resolves (design/spells.txt, "SPELLS";
    the codec leaves it out at 1)."""

    id: ThreatId
    base: int
    members: int = 1
