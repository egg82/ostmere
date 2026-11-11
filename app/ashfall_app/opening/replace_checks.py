"""The check on `replaced_by` (entries.UnlockEntry): only a `retired` unlock names one, and the same outcome unlocks that
card. Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def check_replacements(o: "Opening") -> None:
    for where, out in outcomes(o):
        unlocked_cards = {u.id for u in out.unlocks if u.unlock_kind == "card"}
        for u in out.unlocks:
            if u.replaced_by is None:
                continue
            if u.unlock_kind != "retired":
                fail(where, f"replaced_by is on a {u.unlock_kind} unlock of {u.id}: only a retired unlock has one")
            elif u.replaced_by not in unlocked_cards:
                fail(where, f"{u.id} is replaced by {u.replaced_by}, which the same outcome does not unlock")
    for u in o.start:
        if u.replaced_by is not None:
            fail("start", f"replaced_by is on the start unlock of {u.id}: only an outcome's retired unlock has one")
