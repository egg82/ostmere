"""The opening's whole-game settings read once from opening.toml: when repeats are offered, the journal's habits, and
the first mix."""
from typing import Self

from pydantic import Field, model_validator

from .entries import Entry


class RepeatOffersEntry(Entry):
    """When doing a thing by hand again and again makes it offered as a mix or a rule (api/CONTRACT.txt, "Repeats"):
    a count reached within a span of game time."""

    hand_taps: int = Field(ge=2)
    hand_taps_within_s: int = Field(ge=1)
    switches: int = Field(ge=2)
    switches_within_s: int = Field(ge=1)


class FadeEntry(Entry):
    """A kind's care on its first telling, and what each telling multiplies it by."""

    base: float = Field(gt=0, le=1)
    fade: float = Field(gt=0, lt=1)


class WorryEntry(Entry):
    """A worry's care on its first day, and what each further day in a row adds to it."""

    base: float = Field(gt=0, le=1)
    press: float = Field(gt=0)


class JournalHabitsEntry(Entry):
    """The numbers the journal's habits are decided by (docs/design/journal.md, "The habits as data"). The must kinds
    (a beat, a person, a routine's first telling) carry none: they are always written."""

    routine: FadeEntry
    worry: WorryEntry
    crowd: FadeEntry
    floor: float = Field(ge=0, lt=1)
    """Diligence's lowest share."""
    halflife: float = Field(gt=0)
    """The settledness at which diligence is halfway to its floor."""
    beat_refresh: float = Field(ge=0)
    lines_start: int = Field(ge=1)
    lines_floor: int = Field(ge=1)
    lines_halflife: float = Field(gt=0)
    busy_ratio: float = Field(ge=1)
    late_rate: float = Field(ge=0, le=1)
    misremember_rate: float = Field(ge=0, le=1)
    correct_after_days: int = Field(ge=1)

    @model_validator(mode="after")
    def _budget_falls(self) -> Self:
        if self.lines_floor > self.lines_start:
            raise ValueError("journal_habits: lines_floor is over lines_start, so the budget would grow")
        return self


class FirstMixEntry(Entry):
    """The first mix the page offers once `feature` is unlocked: these hands cards at an even split, made by the
    player's tap (api/CONTRACT.txt)."""

    feature: str
    cards: list[str]

