"""The check on retired chores (week-three-plan item 3; engine DESIGN.txt, "Retired chores", "Content"): only a season's
turn retires orders, and only on a chore's cure, a chore being a chip whose store only a season's standing makes.
Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from ..engine import CardId, Rules
from ..engine.cure_reading import cures_chip
from .chores import chores as chore_chips
from .refs import fail, need, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def check_retired_chores(o: "Opening") -> None:
    """Each outcome naming retire_orders is a trigger's with `season`, and each card it names cures a chore's chip."""
    named = [(where, out.retire_orders) for where, out in outcomes(o) if out.retire_orders]
    if not named:
        return
    seasons = {f"trigger {t.id}" for t in o.triggers if t.season}
    cards = [c.id for c in o.cards]
    for where, retired in named:
        if where not in seasons:
            fail(where, "retires orders but is not a season's turn" if where.startswith("trigger ")
                 else "retires orders outside a season's turn")
        for card in retired:
            need(where, "card", card, cards)


def check_retired_cures(o: "Opening", rules: Rules) -> None:
    """Each card an outcome retires orders on cures a chore's chip. It reads the built rules, so it is a content check:
    a chore's chip may come with a later chapter."""
    named = [(where, out.retire_orders) for where, out in outcomes(o) if out.retire_orders]
    chores = chore_chips(o, rules)
    for where, retired in named:
        for card in retired:
            if not any(cures_chip(rules, CardId(card), chip) for chip in chores):
                fail(where, f"retires the orders on {card}, which cures no chip whose store only a season's standing "
                     "makes")

