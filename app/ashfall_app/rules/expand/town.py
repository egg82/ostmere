"""Town cards, defined once (Catalogue): a `[[town_cards]]` entry is a card's fields plus `lanes` and an id pattern
holding `{lane}`, and the loader expands it to one ordinary CardEntry per lane. The engine sees only the cards.

An entry stays on the Opening once merged. A lane no chapter has declared yet waits, and expands in the chapter that
declares it, so a lane joins by appending to an entry's `lanes`. A lane's cards sit together, after its first
hand-written card (appended when it has none): the order of `cards` is part of the rules digest."""
from pydantic import Field, model_validator

from ...engine import HANDS
from ..entries.entries import CardEntry

LANE_TOKEN = "{lane}"


class TownCardEntry(CardEntry):
    """A CardEntry whose `id` is a pattern and whose `lane` is each of `lanes`."""

    lanes: list[str] = Field(min_length=1)
    """The people who take the job. Never a crew: a crew takes it by `kinds`."""
    kinds: list[str] | None = None
    """The kinds of work this job is. Each crew whose lane `kind` is one of them takes the job. Every job a crew member can
    do says it: `[]` is the explicit "not crew work", and none set is refused (rules/groups.py, check_crew_work)."""
    own: list[str] = []
    """Lanes of `lanes` whose copy of this card is written by hand (a card of the same id on that lane): nothing is
    expanded for them."""

    @model_validator(mode="after")
    def _pattern(self) -> "TownCardEntry":
        if LANE_TOKEN not in self.id:
            raise ValueError(f"town card id {self.id!r} needs {LANE_TOKEN} in it")
        if self.lane != "hands":
            raise ValueError(f"town card {self.id!r}: the lane is each of `lanes`, so `lane` is not set")
        return self

    def card(self, lane: str) -> CardEntry:
        fields = self.model_dump(exclude={"lanes", "own", "kinds"})
        fields["requires"] = [{**r, "id": r["id"].replace(LANE_TOKEN, lane)} if r["id"] is not None else r
                              for r in fields["requires"]]
        return CardEntry.model_validate({**fields, "id": self.id.replace(LANE_TOKEN, lane), "lane": lane})


def expand(
    cards: list[CardEntry], entries: list[TownCardEntry], declared: set[str], fresh_lanes: set[str], fresh: int,
    crew_kinds: dict[str, str],
) -> list[CardEntry]:
    """`cards` with the town cards that are due added. A lane takes an entry when the entry lists it, or the lane is a crew
    (in `crew_kinds`, with its kind) of one of the entry's kinds. Due: a lane in `declared` that is in `fresh_lanes`, for
    every entry; or, for the last `fresh` entries, every lane in `declared`. A collision shows as a duplicate id in the
    result, which check_opening refuses naming it."""
    out = list(cards)
    first_new = len(entries) - fresh
    for lane in sorted(declared | {HANDS}):
        due = [e for i, e in enumerate(entries)
               if takes(e, lane, crew_kinds) and lane not in e.own and (lane in fresh_lanes or i >= first_new)]
        made = [e.card(lane) for e in due]
        if made:
            at = next((i + 1 for i, c in enumerate(out) if c.lane == lane), len(out))
            out[at:at] = made
    return out


def takes(entry: TownCardEntry, lane: str, crew_kinds: dict[str, str]) -> bool:
    return lane in entry.lanes or crew_kinds.get(lane) in (entry.kinds or ())


def undeclared_lanes(entries: list[TownCardEntry], declared: set[str]) -> list[str]:
    """Lanes an entry names that nothing declares: a typo would otherwise expand to nothing, silently."""
    return sorted({lane for e in entries for lane in e.lanes} - declared - {HANDS})
