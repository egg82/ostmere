"""The segment a store moves along from save.time: its saved Segment, plus the work of the cards whose lumps move it
(DESIGN.txt, "Rate form"). Above rates in the import order: the flow part is read from the rates, never from the
saved rate, which a save written before lumps were paid by work rounded with its lumps in."""
from .counts import work_segment
from .ids import StoreId
from .lumps import NO_TERMS, lump_terms, motion, moving_lumps
from .memo import SaveMemo
from .rates import flow_net, running
from .rules import Rules
from .segments import Segment
from .state import Save

_SEGMENTS: SaveMemo[dict[StoreId, Segment]] = SaveMemo(4)


def store_segment(save: Save, rules: Rules, store: StoreId) -> Segment:
    """The segment `store` moves along from save.time until the next event: what every reader samples and solves.

    The save keeps a store's plain Segment: start, value, the slope rounded down and the limit. When cards' lumps
    move the store, the slope is not whole, so this adds back their work from the save's cards and the flow lines'
    net from the rates (a LumpSegment). A store held still (rate 0, no limit: at its cap or
    with an exact net of 0) is its plain Segment."""
    return _SEGMENTS.get(save, rules, lambda: _segments(save, rules))[store]


def keep_segments(save: Save, rules: Rules, found: dict[StoreId, Segment]) -> None:
    """`found` is what store_segment gives for each of the save's stores: rebuild and shift have it already."""
    _SEGMENTS.put(save, rules, found)


def _segments(save: Save, rules: Rules) -> dict[StoreId, Segment]:
    found: dict[StoreId, Segment] = {}
    terms = lump_terms(save, rules)
    for st in save.stores:
        if st.store in found:
            continue
        held = st.segment.rate == 0 and st.segment.limit is None
        den, lumps = (1, ()) if held else moving_lumps(terms.get(st.store, NO_TERMS), lambda c: work_segment(save, c))
        flow = flow_net(save, rules, running(save, rules), st.store) if lumps else 0
        found[st.store] = motion(st.segment, flow, den, lumps)
    return found
