"""Town cards, defined once (Catalogue): a `[[town_cards]]` entry is a card's fields plus `lanes` and an id pattern
holding `{lane}`, and the loader expands it to one ordinary CardEntry per lane. The engine sees only the cards.

An entry stays on the Opening once merged. A lane no chapter has declared yet waits, and expands in the chapter that
declares it, so a lane joins by appending to an entry's `lanes`. A lane's cards sit together, after its first
hand-written card (appended when it has none): the order of `cards` is part of the rules digest."""
from pydantic import Field, model_validator

from ..engine import HANDS
from .entries import CardEntry

LANE_TOKEN = "{lane}"


class TownCardEntry(CardEntry):
    """A CardEntry whose `id` is a pattern and whose `lane` is each of `lanes`."""

    lanes: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _pattern(self) -> "TownCardEntry":
        if LANE_TOKEN not in self.id:
            raise ValueError(f"town card id {self.id!r} needs {LANE_TOKEN} in it")
        if self.lane != "hands":
            raise ValueError(f"town card {self.id!r}: the lane is each of `lanes`, so `lane` is not set")
        return self

    def card(self, lane: str) -> CardEntry:
        fields = self.model_dump(exclude={"lanes"})
        return CardEntry.model_validate({**fields, "id": self.id.replace(LANE_TOKEN, lane), "lane": lane})


def expand(
    cards: list[CardEntry], entries: list[TownCardEntry], declared: set[str], fresh_lanes: set[str], fresh: int,
) -> list[CardEntry]:
    """`cards` with the town cards that are due added. Due: a lane in `declared` that is in `fresh_lanes`, for every
    entry; or, for the last `fresh` entries, every lane in `declared`. A collision shows as a duplicate id in the
    result, which check_opening refuses naming it."""
    out = list(cards)
    first_new = len(entries) - fresh
    for lane in sorted(declared | {HANDS}):
        due = [e for i, e in enumerate(entries) if lane in e.lanes and (lane in fresh_lanes or i >= first_new)]
        made = [e.card(lane) for e in due]
        if made:
            at = next((i + 1 for i, c in enumerate(out) if c.lane == lane), len(out))
            out[at:at] = made
    return out


def undeclared_lanes(entries: list[TownCardEntry], declared: set[str]) -> list[str]:
    """Lanes an entry names that nothing declares: a typo would otherwise expand to nothing, silently."""
    return sorted({lane for e in entries for lane in e.lanes} - declared - {HANDS})
