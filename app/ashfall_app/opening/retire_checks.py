"""The check on retired chores (week-three-plan item 3; engine DESIGN.txt, "Retired chores", "Content"): only a season's
turn retires orders, and only on a chore's cure, a chore being a chip whose store only a season's standing makes.
Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from ..engine import AtLeast, AtMost, CardId, ChipId, Rules, StoreValue
from ..engine.cure_reading import cures_chip
from .convert import build_rules
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
    rules = build_rules(o)
    chores = _chores(rules, _season_standing(o))
    for where, retired in named:
        for card in retired:
            if not any(cures_chip(rules, CardId(card), chip) for chip in chores):
                fail(where, f"retires the orders on {card}, which cures no chip whose store only a season's standing "
                     "makes")


def _season_standing(o: "Opening") -> set[str]:
    """The standing actions some season's turn unlocks."""
    return {u.id for t in o.triggers if t.season for u in t.outcome.unlocks if u.unlock_kind == "action"}


def _chores(rules: Rules, seasonal: set[str]) -> list[ChipId]:
    """The chips watching a store that has a maker, every one of them (cards and standing actions alike) a season's
    standing."""
    found: list[ChipId] = []
    for chip in rules.chips:
        when = chip.when
        if not isinstance(when, (AtLeast, AtMost)) or not isinstance(when.subject, StoreValue):
            continue
        store = when.subject.store
        makers = {str(a.id) for a in rules.standing if any(f.store == store for f in a.makes)}
        makers |= {str(c.id) for c in rules.cards if any(f.store == store for f in c.makes)}
        if makers and makers <= seasonal:
            found.append(chip.id)
    return found
