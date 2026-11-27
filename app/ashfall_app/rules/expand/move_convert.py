"""People's moves as the engine's parts: an outcome's joins, marks, leaves and casts. Pure."""
from typing import TYPE_CHECKING

from ...engine import ActionId, Cast, CastPick, CardId, FeatureId, Join, Leave, LaneId, Mark, MixId

if TYPE_CHECKING:
    from ..entries.move_entries import CastEntry, JoinEntry, LeaveEntry, MarkEntry


def joins(entries: "list[JoinEntry]") -> tuple[Join, ...]:
    return tuple(Join(LaneId(j.lane), MixId(j.mix), None if j.card is None else CardId(j.card), j.own_split)
                 for j in entries)


def marks(entries: "list[MarkEntry]") -> tuple[Mark, ...]:
    return tuple(Mark(LaneId(k.lane), k.own_split, None if k.card is None else CardId(k.card)) for k in entries)


def leaves(entries: "list[LeaveEntry]") -> tuple[Leave, ...]:
    return tuple(Leave(LaneId(x.lane), tuple(ActionId(a) for a in x.stops)) for x in entries)


def casts(entries: "list[CastEntry]") -> tuple[Cast, ...]:
    return tuple(Cast(c.role, tuple(CastPick(LaneId(p.lane), FeatureId(p.feature),
                                             tuple(None if x is None else CardId(x) for x in p.counted))
                                    for p in c.picks))
                 for c in entries)
