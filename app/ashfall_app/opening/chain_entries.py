"""A card's chain (entries.CardEntry.chain; engine design/spells.txt, "SPELLS"): kept apart from entries.py, which is at its
size limit."""
from pydantic import BaseModel, ConfigDict, Field


class ChainEntry(BaseModel):
    """At each completion the card resolves up to `reach` of `runner`'s due fights (a standing fight on a threat with
    `members` of 2 or more), each a won link whose line is link_line_keys[min(i, n) - 1] for link i from 1. reach is the
    base, before any modifier aimed at the card's chain (target "chain")."""

    model_config = ConfigDict(extra="forbid")

    runner: str
    reach: int = Field(ge=1)
    link_line_keys: list[str] = Field(min_length=1)
