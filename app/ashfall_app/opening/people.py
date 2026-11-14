"""People's coming and going as story (LaneEntry.told; docs/decisions/people.md, "People, as built"). A `line` person is
written by the story lines of the outcome that joins or leaves them, which the content authors and people_checks.py
requires. A `mention` person is written by no line of their own: the loader gives each outcome that joins or leaves
one a mention line, keyed by the lane and the way, with no text and kind story, and the page counts a day's mentions
into one line worded from the `[people]` bands (api/CONTRACT.txt, "People"). A mention is in the save's log like any
line, so the chronicle places it at the second it happened."""
from collections.abc import Iterator
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .entries import Entry, OutcomeEntry

if TYPE_CHECKING:
    from .schema import Opening

Way = Literal["joined", "left"]


class BandEntry(Entry):
    """The lines for a day on which at least `at_least` people came (or went), until the next band's: one is drawn
    for each such day by a seeded shuffle of `keys`."""

    at_least: int = Field(ge=1)
    keys: list[str] = Field(min_length=1)


class PeopleEntry(Entry):
    """[people], declared once in the content: the bands a day's mention is worded from, by how many came and went."""

    came: list[BandEntry] = Field(min_length=1)
    went: list[BandEntry] = Field(min_length=1)


def mention_key(way: Way, lane: str) -> str:
    return f"people.{way}.{lane}"


def moves(out: OutcomeEntry) -> Iterator[tuple[Way, str]]:
    """Each person the outcome joins or leaves. A counted join is not one: that person came earlier, and was told then."""
    for j in out.joins:
        if not j.counted:
            yield "joined", j.lane
    for x in out.leaves:
        yield "left", x.lane


def told(o: "Opening", how: Literal["line", "mention"]) -> set[str]:
    return {x.id for x in o.lanes if x.told == how}


def mention_keys(o: "Opening") -> dict[str, tuple[Way, str]]:
    """Every mention line the content can write, to the way and the lane it counts."""
    mention = told(o, "mention")
    return {mention_key(w, lane): (w, lane) for out in _outcomes(o) for w, lane in moves(out) if lane in mention}


def person_keys(o: "Opening") -> set[str]:
    """The story lines that tell a `line` person joining or leaving: those of the outcomes that move one."""
    line = told(o, "line")
    return {k for out in _outcomes(o) if any(lane in line for _, lane in moves(out))
            for k in out.line_keys if o.line_kinds.get(k) == "story"}


def with_mentions(o: "Opening") -> "Opening":
    """`o` with each outcome that moves a mention person ending in that person's mention line, the line's kind story and
    its text empty: the page words it."""
    mention = told(o, "mention")
    if not mention:
        return o
    added = sorted(mention_keys(o))
    clash = [k for k in added if k in o.text]
    if clash:
        raise ValueError(f"text: keys a mention line takes: {clash}")

    def out(x: OutcomeEntry) -> OutcomeEntry:
        keys = [mention_key(w, lane) for w, lane in moves(x) if lane in mention]
        return x.model_copy(update={"line_keys": [*x.line_keys, *keys]}) if keys else x

    return o.model_copy(update={
        "triggers": [t.model_copy(update={"outcome": out(t.outcome)}) for t in o.triggers],
        "offers": [x.model_copy(update={"answers": [a.model_copy(update={"outcome": out(a.outcome)}) for a in x.answers]})
                   for x in o.offers],
        "text": {**o.text, **{k: "" for k in added}},
        "line_kinds": {**o.line_kinds, **{k: "story" for k in added}},
    })


def _outcomes(o: "Opening") -> Iterator[OutcomeEntry]:
    """The outcomes that may move a person: a trigger's and an answer's."""
    yield from (t.outcome for t in o.triggers)
    yield from (a.outcome for x in o.offers for a in x.answers)
