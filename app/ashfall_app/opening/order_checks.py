"""An order card is a rule that taps a card or switches the mix when a store reaches a level; what makes one sound."""
from typing import TYPE_CHECKING

from ..engine import QUANTITY_SCALE, units
from .chip_checks import check_chip_card
from .convert import levels
from .refs import fail, need, offer_cap

if TYPE_CHECKING:
    from .entries import OrderCardEntry
    from .schema import Opening


def check_order_cards(o: "Opening", ids: dict[str, list[str]]) -> None:
    """Each order card names a known store and exactly one of tap_card and switch_mix, with a `when` on its own store.
    `ids` is ids_by_kind(o)."""
    for oc in o.order_cards:
        where = f"order card for {oc.store}"
        need(where, "store", oc.store, ids["store"])
        if (oc.tap_card is None) == (oc.switch_mix is None):
            fail(where, "needs exactly one of tap_card and switch_mix")
        if oc.tap_card is not None:
            need(where, "card", oc.tap_card, ids["card"])
        if (oc.when.subject_kind, oc.when.id) != ("store", oc.store) or oc.when.test == "after_time":
            fail(where, "its when must be an at_most or at_least on its own store (the page words it as a level on "
                         "that store)")
        if oc.when.every != 1:
            fail(where, "its when has every: a rule's levels are whole items")
        cap = next((s.cap_items for s in o.stores if s.id == oc.store), None)
        if oc.when.test == "at_least":
            _check_rising_card(o, where, oc, cap)
        elif cap is not None and oc.when.release is not None \
                and levels(oc.when)[1] >= offer_cap(o, oc.store, oc.offered_after) * QUANTITY_SCALE:
            fail(where, "its release is at or past the store's cap when it is offered, so the rule would never let go")
        check_chip_card(o, where, oc)


def _check_rising_card(o: "Opening", where: str, oc: "OrderCardEntry", cap: int | None) -> None:
    """An at_least card is the rule for a full or rising line, or for a chip that shows while its store is high: it taps
    a card that takes that store (so the rule spends what fills), comes on at a level the store can reach, and lets go
    above 0 (a store never goes under 0)."""
    card = next((c for c in o.cards if c.id == oc.tap_card), None)
    if card is None:
        fail(where, "an at_least card taps a card")
    if not any(a.store == oc.store for a in card.inputs) and not any(f.store == oc.store for f in card.costs):
        fail(where, f"card {card.id} does not take {oc.store}, so the rule would not spend what fills")
    if cap is not None and levels(oc.when)[0] > units(cap):
        fail(where, "its value is past the store's cap, so the rule would never come on")
    if oc.when.release is not None and levels(oc.when)[1] < units(1):
        fail(where, "its release is under one, so the rule would never let go")
