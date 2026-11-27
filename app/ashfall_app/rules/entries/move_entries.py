"""What an outcome does to the people: joins, marks, leaves and casts (engine Join, Mark, Leave, Cast)."""
from pydantic import Field, model_validator

from .entry_base import Entry


class JoinEntry(Entry):
    """A person joins the town (engine Join): the ruled lane `lane`'s person is present from now on, and the lane's
    always task becomes its share in the town mix `mix` (an id beginning "town:"). `card` is the share when the lane has
    no uncapped always rule. `counted`: a tally counted this person when they arrived, so the join adds none."""

    lane: str
    mix: str
    card: str | None = None
    counted: bool = False
    own_split: bool
    """Whether the person keeps their own split as they arrive: authored on every join, never defaulted. False needs
    the lane to have a `group`, and `card` (if any) is then a card on that group."""


class MarkEntry(Entry):
    """A joined person's mark set or cleared (engine Mark): `own_split` False hands the person to their lane's `group`;
    `card` is an uncapped card given a share when the town mix holds none on its lane: on the person's own lane when
    the mark is set, on their group when it is cleared."""

    lane: str
    own_split: bool
    card: str | None = None


class LeaveEntry(Entry):
    """A person leaves the town for good (engine Leave): the ruled lane `lane`'s person is gone, and each standing
    action in `stops` stops with them."""

    lane: str
    stops: list[str] = []


class CastPickEntry(Entry):
    """One lane a role may go to, and the card each of the cast's patterns counts on it (None: no such card)."""

    lane: str
    feature: str
    counted: list[str | None]


class CastEntry(Entry):
    """A role given to one person at the outcome's instant (engine Cast; api/contract/casting.txt, "CASTING"): the eligible
    single lane with the most completions of the first pattern's card, ties and none going to the next pattern, then
    the earliest declared. `patterns` are town-card id patterns, written with their {lane}, in priority order."""

    role: str
    patterns: list[str] = Field(min_length=1)
    picks: list[CastPickEntry] = []
    """Filled by the loader (casts.py), never authored."""

    @model_validator(mode="before")
    @classmethod
    def _no_authored_picks(cls, data: dict[str, object]) -> dict[str, object]:
        if "picks" in data:
            raise ValueError("a cast's picks are the loader's: author the role and its patterns")
        return data
