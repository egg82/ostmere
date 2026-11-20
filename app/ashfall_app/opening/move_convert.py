"""People's moves as the engine's parts: an outcome's joins, marks and leaves. Pure."""
from typing import TYPE_CHECKING

from ..engine import ActionId, CardId, Join, Leave, LaneId, Mark, MixId

if TYPE_CHECKING:
    from .entries import JoinEntry, LeaveEntry, MarkEntry


def joins(entries: "list[JoinEntry]") -> tuple[Join, ...]:
    return tuple(Join(LaneId(j.lane), MixId(j.mix), None if j.card is None else CardId(j.card), j.own_split)
                 for j in entries)


def marks(entries: "list[MarkEntry]") -> tuple[Mark, ...]:
    return tuple(Mark(LaneId(k.lane), k.own_split, None if k.card is None else CardId(k.card)) for k in entries)


def leaves(entries: "list[LeaveEntry]") -> tuple[Leave, ...]:
    return tuple(Leave(LaneId(x.lane), tuple(ActionId(a) for a in x.stops)) for x in entries)
