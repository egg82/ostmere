"""The chips' checks: a chip says what it costs, and a chip's order card answers its chip. Raises ValueError naming
the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .entries import OrderCardEntry
    from .schema import Opening


def check_chips(o: "Opening") -> None:
    """A chip that changes something says what (cost_key), and is drawn whenever it changes it (no offered_after)."""
    for ch in o.chips:
        if bool(ch.effects) != (ch.cost_key is not None):
            fail(f"chip {ch.id}", "a chip has a cost_key exactly when it has effects")
        if ch.effects and ch.offered_after is not None:
            fail(f"chip {ch.id}", "has effects and an offered_after, so its cost runs before it is drawn")


def check_chip_card(o: "Opening", where: str, oc: "OrderCardEntry") -> None:
    """A chip's order card: the chip exists, watches the card's store, has the card's `when` exactly (the page
    words the rule as the chip) and no off_line_key; after_end only on such a card."""
    if oc.chip is None:
        if oc.after_end:
            fail(where, "after_end needs a chip: only a chip's card is offered in the hands strip")
        return
    chip = next((c for c in o.chips if c.id == oc.chip), None)
    if chip is None:
        fail(where, f"unknown chip {oc.chip}")
    if (chip.when.subject_kind, chip.when.id) != ("store", oc.store):
        fail(where, f"chip {oc.chip} does not watch its store {oc.store}")
    if chip.when != oc.when:
        fail(where, f"its when is not chip {oc.chip}'s, so the rule would not read as the chip")
    if chip.off_line_key is not None:
        fail(f"chip {chip.id}", "has an order card and an off_line_key: the rule clears it every cycle and the line "
             "repeats each time; say the first cure with a trigger instead")
