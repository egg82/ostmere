"""The loader's checks on the world map's places (api/contract/map.txt, "MAP"), each naming the place: its reveal and its
labelled_after are unlocks something in the content adds, and no two places share a cell, the town's included, unless one
is declared `over` the other. A label's key is the text checks'. Raises ValueError naming the place."""
from typing import TYPE_CHECKING

from ...casts import cast_unlocks
from ...entries.map_entries import MAP_REACH
from ...refs import fail, ids_by_kind, need, outcomes

if TYPE_CHECKING:
    from ...entries.entries import UnlockEntry
    from ...schema import Opening

REVEALS = ("feature", "card", "skill", "store", "chip", "action", "entry")
"""The unlock kinds a place may be revealed or labelled by: each is added by an authored outcome or the start, or (an entry)
by its first note, so whether anything adds it is checkable from the content."""


def check_places(o: "Opening") -> None:
    ids = ids_by_kind(o)
    added = {(u.unlock_kind, u.id) for _, out in outcomes(o) for u in out.unlocks} | {(u.unlock_kind, u.id) for u in o.start}
    added |= {unlock for _, unlock in cast_unlocks(o)}

    def check_unlock(where: str, field: str, u: "UnlockEntry") -> None:
        if u.unlock_kind not in REVEALS:
            fail(where, f"a {field} is one of {', '.join(REVEALS)}, not {u.unlock_kind}")
        need(where, u.unlock_kind, u.id, ids[u.unlock_kind])
        if u.unlock_kind != "entry" and (u.unlock_kind, u.id) not in added:
            fail(where, f"nothing unlocks its {field} {u.unlock_kind} {u.id}, so it would never happen")

    taken: dict[tuple[int, int], str] = {(0, 0): "the town"}
    for p in o.places:
        where = f"place {p.id}"
        check_unlock(where, "reveal", p.reveal)
        if p.labelled_after is not None:
            if p.label_key is None:
                fail(where, "labelled_after on a place with no label_key labels nothing")
            check_unlock(where, "labelled_after", p.labelled_after)
        if any(abs(v) > MAP_REACH for v in p.at):
            fail(where, f"at {list(p.at)} is past the map's reach of {MAP_REACH} cells")
        if p.over is None:
            if p.at in taken:
                fail(where, f"at {list(p.at)} is already {taken[p.at]}'s cell")
            taken[p.at] = where
    stacked: dict[str, str] = {}
    by_id = {p.id: p for p in o.places}
    for p in o.places:
        if p.over is None:
            continue
        where = f"place {p.id}"
        base = by_id.get(p.over)
        if base is None:
            fail(where, f"over names {p.over}, which is no place")
        if base.over is not None:
            fail(where, f"over names {p.over}, which is itself over another place")
        if base.at != p.at:
            fail(where, f"at {list(p.at)} is not {p.over}'s cell {list(base.at)}, so it is not over it")
        if p.over in stacked:
            fail(where, f"over {p.over}, which place {stacked[p.over]} already sits on")
        stacked[p.over] = p.id
