"""The content's lanes and the town's later names, whose labels change with the unlocks (contract/, "A lane run by
rules", "The town's mix")."""
from .. import engine as e
from ..opening import convert as authored
from ..opening.casts import casts
from ..opening.lane_entries import LaneLabelEntry
from ..opening.schema import Opening
from . import content_models as cm
from . import convert


def later_labels(labels: list[LaneLabelEntry]) -> list[cm.LaneLabel]:
    return [cm.LaneLabel(after=convert.unlock(authored.unlock(lb.after)), label_key=lb.label_key) for lb in labels]


def lane_infos(o: Opening) -> list[cm.LaneInfo]:
    hands = cm.LaneInfo(lane=e.HANDS, label_key=o.hands_label_key, ruled=False, later_labels=[], name_key=None, told=None,
                        pooled=False, group=None, tied=None, station=False)
    return [hands, *(cm.LaneInfo(lane=x.id, label_key=x.label_key, ruled=x.ruled, later_labels=later_labels(x.later_labels),
                                 name_key=x.name_key, told=x.told, pooled=x.pooled, group=x.group,
                                 tied=x.tied, station=x.station) for x in o.lanes)]


def cast_infos(o: Opening) -> list[cm.CastInfo]:
    """Each role, once, with each candidate lane and the feature its cast unlocks (the loader's picks)."""
    found: dict[str, cm.CastInfo] = {}
    for _, c in casts(o):
        found.setdefault(c.role, cm.CastInfo(role=c.role, lanes=[cm.CastLane(lane=p.lane, feature=p.feature) for p in c.picks]))
    return list(found.values())
