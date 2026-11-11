"""Wire models of the fights (CONTRACT.txt, "FIGHTS"): the view's, and the content's sides and threats; the conventions
in models.py hold here."""
from enum import StrEnum

from pydantic import BaseModel


class StrengthKind(StrEnum):
    BASE = "base"
    ADD_BP = "add_bp"
    MUL_BP = "mul_bp"


class StrengthEntry(BaseModel):
    """One source behind a strength: the base (source null), a sum entry (+1500 is +15%) or a factor (15000 is x1.5)."""

    source: str | None
    form: StrengthKind
    amount_bp: int
    share_bp: int | None
    """Set only on an entry a card holds while it runs: `source` is then the card's id, `share_bp` its share of its
    lane's time now, `amount_bp` what that share gives. Null on every other entry."""


class Strength(BaseModel):
    """A side's power or a threat's strength: `value` is what the engine uses; `sources` are every source behind it, the
    base first, then the sum entries, then the factors, each in stack order (CONTRACT.txt, "FIGHTS")."""

    value: int
    sources: list[StrengthEntry]


class Fight(BaseModel):
    """One unlocked fight card or standing action, now (CONTRACT.txt, "FIGHTS")."""

    runner: str
    side: str
    threat: str
    power: Strength
    threat_strength: Strength
    loss_bp: int
    """The share of fights lost now, 1 to 10000; for a running tap, the share it was started at and pays to its end."""
    fought: int
    lost: int
    """Whole fights since the runner first ran; lost <= fought."""


class SideInfo(BaseModel):
    side: str
    label_key: str


class ThreatInfo(BaseModel):
    threat: str
    label_key: str
