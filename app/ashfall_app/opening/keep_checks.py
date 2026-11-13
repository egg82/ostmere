"""The check on a need a rule keeps: a store that drains and is kept by an "under x, until y" order card sits between
x and y, reaching y only for the moment the rule lets go. A card that requires y or more of it is ready only at that
moment, with no ready time to queue on while the store drains (docs/design/opening-screen.md, "When ready"), so a
player the rules carry finds it unready at every return. Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening


def kept_levels(o: "Opening") -> dict[str, int]:
    """Each store some at_most order card keeps, with the highest level any of them lets go at."""
    found: dict[str, int] = {}
    for oc in o.order_cards:
        if oc.when.test == "at_most" and oc.when.subject_kind == "store":
            found[oc.store] = max(found.get(oc.store, 0), oc.when.release or oc.when.value)
    return found


def check_kept_needs(o: "Opening") -> None:
    """No card requires, of a store a standing action drains, as much as or more than the rule keeping it lets go at."""
    drained = {f.store for a in o.standing for f in a.costs}
    kept = kept_levels(o)
    for card in o.cards:
        for r in card.requires:
            if r.test != "at_least" or r.subject_kind != "store" or r.id not in drained or r.id not in kept:
                continue
            if r.value >= kept[r.id]:
                fail(f"card {card.id}", f"it requires {r.value} {r.id} and the rule keeping {r.id} lets go at "
                     f"{kept[r.id]} while it drains, so the need is met only for the moment the rule lets go")
