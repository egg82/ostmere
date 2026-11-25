"""Which stores only feed a bonus: the content read as the page's StoreInfo.bonus_bp needs it. Pure."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import Opening


def bonus_bp(o: "Opening", store: str) -> int | None:
    """The lane speed change the store's eaters hold while they run, when every runner that takes from the store is an
    eater holding one (engine DESIGN.txt, "HELD SPEED"): the store only feeds a bonus. An eater is a standing action, or
    a card on a station lane (the pot) that makes nothing. The first eater's first such change; None when anything else
    takes from it or nothing does."""
    stations = {x.id for x in o.lanes if x.station}
    fed = [c for c in o.cards if c.lane in stations and not c.makes and not c.outcome.stores]
    takers = [c for c in o.cards if c not in fed and (any(a.store == store for a in (*c.inputs, *c.drains))
              or any(f.store == store for f in c.costs) or (c.fight is not None and any(a.store == store for a in c.fight.loses)))]
    eaters = [a for a in (*o.standing, *fed) if any(f.store == store for f in a.costs)
              or (a.fight is not None and any(x.store == store for x in a.fight.loses))]
    speeds = [[w.amount_bp for w in a.while_running if w.lane is not None] for a in eaters]
    if takers or not eaters or not all(speeds):
        return None
    return speeds[0][0]
