"""Who asks an offer and what it says of itself (api/contract/offers.txt, "OFFERS"): askers are ruled lanes, each once, no
offer says it expires while the engine cannot make it go, and what an offer's `gates_read_feature` promises holds."""
from typing import TYPE_CHECKING

from ...refs import conditions, fail, need

if TYPE_CHECKING:
    from ...schema import Opening


def check_asks(o: "Opening") -> None:
    """Fails, naming the offer, for an asker that is not a ruled lane, an asker named twice, and an expiry_key."""
    ruled = {lane.id for lane in o.lanes if lane.ruled}
    check_gates_read_feature(o)
    for x in o.offers:
        where = f"offer {x.id}"
        for lane in x.askers:
            if lane not in ruled:
                fail(where, f"asker {lane!r} is not a ruled lane, so the page has no person to name")
        if len(set(x.askers)) != len(x.askers):
            fail(where, "names an asker twice")
        if x.expiry_key is not None:
            fail(where, "has an expiry_key, but an offer never goes (engine design/, KNOWN GAPS: offer expiry)")


def check_gates_read_feature(o: "Opening") -> None:
    """Fails, naming the offer, for a listed feature that is unknown or not unlocked by the finish of a card every
    answer unlocks; and, naming the entry, for a condition that reads such an offer as answered or one of its answers."""
    cards = {c.id: c for c in o.cards}
    for x in o.offers:
        if not x.gates_read_feature:
            continue
        where = f"offer {x.id}"
        unlocked = [{u.id for u in a.outcome.unlocks if u.unlock_kind == "card"} for a in x.answers]
        shared = unlocked[0].intersection(*unlocked[1:])
        for f in x.gates_read_feature:
            need(where, "feature", f, [e.id for e in o.features])
            if not any(u.unlock_kind == "feature" and u.id == f for c in shared for u in cards[c].finished.unlocks):
                fail(where, f"feature {f} is not unlocked by the finish of a card every answer unlocks")
        answers = {a.id for a in x.answers}
        for at, c, _ in conditions(o):
            if c.subject_kind == "unlocked" and (c.id in answers if c.unlock_kind == "answer" else
                                                  c.unlock_kind == "answered" and c.id == x.id):
                fail(at, f"reads offer {x.id}'s answer; read {', '.join(x.gates_read_feature)} instead (gates_read_feature)")
