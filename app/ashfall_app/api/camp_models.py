"""The Camp bar on the wire (CONTRACT.txt; re-exported from content_models.py)."""
from pydantic import BaseModel

from .models import Unlock


class CampLevel(BaseModel):
    at: int
    """The camp store's quantity at which this level is reached."""
    pays_key: str
    pays_from: int | None
    pays_to: int | None
    """The number the level pays, before and after, in quantity units; null for a story unlock (the marker shows "?")."""
    change_bp: list[int]
    """The level's modifiers as signed changes in basis points, as LevelPays.change_bp: the slots of pays_key. Empty for a
    held level (its marker is "?"); a text may leave out a slot its pays_from and pays_to already state."""
    held: bool
    """A marker past the opening: the bar fills to it and holds there; the level is never reached here unless
    `lifted_by` lifts it."""
    lifted_by: list[str]
    """The cards any one of whose finish lifts this held level (its cap raise lets the bar fill on and the level
    land); empty for a level nothing lifts."""
    names: list[Unlock]
    """What the level's pays words name (its modifiers' cards, standing actions and stores); none for a held level,
    whose marker is "?". The marker words its pays only once all are in View.unlocked."""


class CampInfo(BaseModel):
    """The bar to work toward: drawn from the ledger line of `store` (never drawn as a ledger line); its level is how
    many of `camp_levels`' `at` the sample has reached (CONTRACT.txt)."""

    store: str
    camp_levels: list[CampLevel]
