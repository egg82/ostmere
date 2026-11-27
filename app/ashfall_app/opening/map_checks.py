"""The loader's checks on the world map's places (api/contract/map.txt, "MAP"), each naming the place: its reveal is an unlock
something in the content adds, and no two places share a cell, the town's included. A label's key is the text checks'.
Raises ValueError naming the place."""
from typing import TYPE_CHECKING

from .casts import cast_unlocks
from .map_entries import MAP_REACH
from .refs import fail, ids_by_kind, need, outcomes

if TYPE_CHECKING:
    from .schema import Opening

REVEALS = ("feature", "card", "skill", "store", "chip", "action", "entry")
"""The unlock kinds a place may be revealed by: each is added by an authored outcome or the start, or (an entry) by its
first note, so whether anything reveals the place is checkable from the content."""


def check_places(o: "Opening") -> None:
    ids = ids_by_kind(o)
    added = {(u.unlock_kind, u.id) for _, out in outcomes(o) for u in out.unlocks} | {(u.unlock_kind, u.id) for u in o.start}
    added |= {unlock for _, unlock in cast_unlocks(o)}
    taken: dict[tuple[int, int], str] = {(0, 0): "the town"}
    for p in o.places:
        where, r = f"place {p.id}", p.reveal
        if r.unlock_kind not in REVEALS:
            fail(where, f"a reveal is one of {', '.join(REVEALS)}, not {r.unlock_kind}")
        need(where, r.unlock_kind, r.id, ids[r.unlock_kind])
        if r.unlock_kind != "entry" and (r.unlock_kind, r.id) not in added:
            fail(where, f"nothing unlocks its reveal {r.unlock_kind} {r.id}, so it would never be revealed")
        if any(abs(v) > MAP_REACH for v in p.at):
            fail(where, f"at {list(p.at)} is past the map's reach of {MAP_REACH} cells")
        if p.at in taken:
            fail(where, f"at {list(p.at)} is already {taken[p.at]}'s cell")
        taken[p.at] = f"place {p.id}"
