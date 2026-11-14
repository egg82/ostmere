"""Who asks an offer and what it says of itself (api/CONTRACT.txt, "OFFERS"): askers are ruled lanes, each once, and no
offer says it expires while the engine cannot make it go."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening


def check_asks(o: "Opening") -> None:
    """Fails, naming the offer, for an asker that is not a ruled lane, an asker named twice, and an expiry_key."""
    ruled = {lane.id for lane in o.lanes if lane.ruled}
    for x in o.offers:
        where = f"offer {x.id}"
        for lane in x.askers:
            if lane not in ruled:
                fail(where, f"asker {lane!r} is not a ruled lane, so the page has no person to name")
        if len(set(x.askers)) != len(x.askers):
            fail(where, "names an asker twice")
        if x.expiry_key is not None:
            fail(where, "has an expiry_key, but an offer never goes (engine DESIGN.txt, KNOWN GAPS: offer expiry)")
