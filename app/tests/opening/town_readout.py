"""The Town view's readout: at each chapter's end, the things the Town view asks the player to tune, by id. A thing is a
person keeping their own split or a group with a joined member who does not; a station (the pot) is neither, and a
person who left is gone. How many is a feel ("five-ish", owner, 2026-11-25), so this reports and fails nothing
(docs/decisions/people.md, "The mark: who keeps their own split"). Ids only (CLAUDE.md, "Never spoil the owner").

    python -m tests.opening.town_readout     # from app/: print it
"""
import sys

from ashfall_app.opening.refs import outcomes
from ashfall_app.opening.schema import CHAPTERS, OPENING, Opening, chapter_ends, load_opening

NAMES = ("town",)


def town_managed(o: Opening) -> tuple[list[str], dict[str, list[str]]]:
    """(people holding their own split, each group with a member: its members), at the end of `o`'s content. A person's
    mark is their last mark's, else whether any join of theirs kept their own split."""
    people = {x.id: x for x in o.lanes if x.ruled and not x.pooled and not x.station}
    joined: dict[str, bool] = {}
    marked: dict[str, bool] = {}
    left: set[str] = set()
    for _, out in outcomes(o):
        for j in out.joins:
            joined[j.lane] = joined.get(j.lane, False) or j.own_split
        for m in out.marks:
            marked[m.lane] = m.own_split
        left |= {x.lane for x in out.leaves}
    here = [x for x in people if x in joined and x not in left]
    own = [x for x in here if marked.get(x, joined[x])]
    groups: dict[str, list[str]] = {}
    for x in here:
        if x not in own and (g := people[x].group) is not None:
            groups.setdefault(g, []).append(x)
    return own, groups


def line(chapter: str, o: Opening) -> str:
    own, groups = town_managed(o)
    crews = " ".join(f"{g}({' '.join(m)})" for g, m in sorted(groups.items()))
    return f"  {chapter:18s} {len(own) + len(groups):2d}  {' '.join(own) or '-'} | {crews or '-'}"


def render(prefixes: list[tuple[str, Opening]]) -> str:
    """One line per chapter end: how many things, the people keeping their own split, then each group and its members."""
    head = "chapter end      things  people keeping their own split | groups (members)"
    return "\n".join([head, *(line(name, o) for name, o in prefixes)])


def readouts() -> dict[str, str]:
    first = load_opening(OPENING, ())
    return {"town": render(list(zip((c.stem for c in CHAPTERS), chapter_ends(first, CHAPTERS))))}


if __name__ == "__main__":
    print(readouts()["town"])
    sys.exit(0)
