"""The opening's whole-game settings read once from opening.toml: when repeats are offered, and the first mix."""
from pydantic import Field

from .entries import Entry


class RepeatOffersEntry(Entry):
    """When doing a thing by hand again and again makes it offered as a mix or a rule (api/CONTRACT.txt, "Repeats"):
    a count reached within a span of game time."""

    hand_taps: int = Field(ge=2)
    hand_taps_within_s: int = Field(ge=1)
    switches: int = Field(ge=2)
    switches_within_s: int = Field(ge=1)


class FirstMixEntry(Entry):
    """The first mix the page offers once `feature` is unlocked: these hands cards at an even split, made by the
    player's tap (api/CONTRACT.txt)."""

    feature: str
    cards: list[str]

