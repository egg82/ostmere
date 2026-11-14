"""The checks on how people's coming and going is written (people.py): every person says `told` and nothing else does;
an outcome that joins or leaves a `line` person writes a story line of its own; a `mention` person has `[people]` bands
to be worded from. Structure only: which keys an outcome writes and their kinds, never their words. Raises ValueError
naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .people import BandEntry, mention_keys, moves, told
from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def check_people(o: "Opening") -> None:
    for x in o.lanes:
        if x.ruled and x.told is None:
            fail(f"lane {x.id}", "is a person with no `told`: say whether their coming and going is a line or a mention")
        if not x.ruled and x.told is not None:
            fail(f"lane {x.id}", "is told but is not a ruled lane: only a person comes and goes")
    line, mentions = told(o, "line"), mention_keys(o)
    for where, out in outcomes(o):
        story = [k for k in out.line_keys if o.line_kinds.get(k) == "story" and k not in mentions]
        for way, lane in moves(out):
            if lane in line and not story:
                fail(where, f"{way} {lane}, a line person, and writes no story line")
    if o.people is None:
        if told(o, "mention"):
            fail(f"lane {sorted(told(o, 'mention'))[0]}", "is a mention, and the content has no [people] bands to word it")
        return
    _check_bands(o, "people came", o.people.came)
    _check_bands(o, "people went", o.people.went)


def _check_bands(o: "Opening", where: str, bands: list[BandEntry]) -> None:
    """The first band starts at one person, each later one at more than the last, and every key is in text."""
    starts = [b.at_least for b in bands]
    if starts[0] != 1 or any(a >= b for a, b in zip(starts, starts[1:])):
        fail(where, "bands start at one person and rise: every count has exactly one band")
    for key in (k for b in bands for k in b.keys):
        if key not in o.text:
            fail(where, f"key {key!r} is not in text")
