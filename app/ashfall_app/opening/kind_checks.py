"""An offer's kind and its answers' roles (engine DESIGN.txt, "OFFER KINDS"): a role exactly where there is a kind,
distinct within an offer, and the same set across the offers of a kind."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening


def check_kinds(o: "Opening") -> None:
    """Fails, naming the offer, for a role on an unkinded offer, a kinded offer's answer with no role, two answers of
    one offer with one role, and two offers of one kind whose role sets differ."""
    roles: dict[str, frozenset[str | None]] = {}
    for x in o.offers:
        have = [a.role for a in x.answers]
        where = f"offer {x.id}"
        if x.kind is None:
            if any(r is not None for r in have):
                fail(where, "an answer has a role but the offer has no kind")
            continue
        if None in have:
            fail(where, "every answer of a kinded offer needs a role")
        if len(set(have)) != len(have):
            fail(where, "two answers share a role")
        if roles.setdefault(x.kind, frozenset(have)) != frozenset(have):
            fail(where, f"its roles differ from the other offers of kind {x.kind}")
