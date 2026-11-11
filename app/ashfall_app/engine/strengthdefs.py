"""The kinds a fight's strengths are read for: who fights and what they fight (DESIGN.txt, "FIGHTS")."""
from dataclasses import dataclass

from .ids import SideId, ThreatId


@dataclass(frozen=True)
class SideDef:
    """A Type Object for one side, by strength: base >= 0 before any entry aimed at its SideStrength."""

    id: SideId
    base: int


@dataclass(frozen=True)
class ThreatDef:
    """A Type Object for one entry of a roster: base > 0 before any entry aimed at its ThreatStrength."""

    id: ThreatId
    base: int
