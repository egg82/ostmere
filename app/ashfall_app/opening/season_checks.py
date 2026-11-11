"""The check on a season's turn (week-two-plan item 6): a trigger marked `season` is an `after_time` trigger; what it
opens draws a pool it fills, and it carries no modifier on a rate. Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening

RATE_TARGETS = ("rate", "work", "lane")


def check_season_turns(o: "Opening") -> None:
    """A card a season's turn opens takes, as an input, a store that turn adds to; a standing action it opens costs
    one. So the season's end retires nothing and greys no mix, and a raise that ended with its season would lower a
    saved mix's rates, so the turn aims no modifier at a rate, a card's work or a lane."""
    cards = {c.id: {a.store for a in c.inputs} for c in o.cards}
    actions = {a.id: {f.store for f in a.costs} for a in o.standing}
    for t in o.triggers:
        if not t.season:
            continue
        if t.when.test != "after_time":
            fail(f"trigger {t.id}", "is a season's turn but its when is not after_time")
        for m in t.outcome.modifiers:
            if m.target in RATE_TARGETS:
                fail(f"trigger {t.id}", f"is a season's turn aimed at a {m.target} ({m.id}): a season adds and raises "
                     "caps, sides and threats, and never moves a rate")
        filled = {a.store for a in t.outcome.stores}
        for u in t.outcome.unlocks:
            pools = cards.get(u.id) if u.unlock_kind == "card" else actions.get(u.id) if u.unlock_kind == "action" else None
            if pools is not None and not pools & filled:
                fail(u.id, f"is opened by the season's turn {t.id} but draws no store that turn fills")
