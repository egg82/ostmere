"""The triggers the loader makes to count answers by role (OfferKindEntry's roles' `tally`). Pure."""
from typing import TYPE_CHECKING

from ..engine import QUANTITY_SCALE, Amount, AtLeast, Outcome, StoreId, TriggerDef, TriggerId, Unlock, Unlocked, UnlockKind

if TYPE_CHECKING:
    from .schema import Opening


def tally_triggers(o: "Opening") -> tuple[TriggerDef, ...]:
    """For each answer of a role that names a tally: once the answer is unlocked, add one to that store. A trigger
    already true when a save is rebased fires then, so an answer given before the tally existed counts."""
    stores = {(k.kind, r.role): r.tally for k in o.offer_kinds for r in k.roles if r.tally is not None}
    return tuple(
        TriggerDef(TriggerId(f"tally_{a.id}"), AtLeast(Unlocked(Unlock(UnlockKind.ANSWER, a.id)), 1, 1),
                   Outcome(stores=(Amount(StoreId(tally), QUANTITY_SCALE),)))
        for x in o.offers for a in x.answers if (tally := stores.get((x.kind or "", a.role or ""))) is not None)
