"""Wire models of a working's chain (contract/spells.txt, "SPELLS"); the conventions in models.py hold here."""
from pydantic import BaseModel

from .fight_models import Strength


class ChainInfo(BaseModel):
    """A card's chain: the standing fight whose due fights it resolves (its threat always a group), and the keys its
    link lines use: link i, from 1, reads link_line_keys[min(i, n) - 1] (contract/spells.txt, "SPELLS")."""

    runner: str
    link_line_keys: list[str]


class Chain(BaseModel):
    """One unlocked card with a chain that is not completed, now (contract/spells.txt, "SPELLS")."""

    card: str
    runner: str
    up_to: Strength
    """The reach now: the most links the card's next completion resolves if nothing lands before it, with its sources
    (the base first, as a Strength's). It only rises."""
