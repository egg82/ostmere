"""The check on an order card's band: a rule on the hands whose hold covers one completion costs a latch turn and a
landing every time (taps on the hands never repeat: engine DESIGN.txt, "REPEATING TAPS", "Who may repeat"), which a
draining store turns into an instant a minute all day. Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from ..engine import HANDS
from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening

BAND_TAPS = 2
"""A band is at least this many completions' yield: the least that lets one hold cover more than one tap. The shipped
hands cards sit at three completions or more."""


def check_bands(o: "Opening") -> None:
    """Each non-chip at_most order card that taps a hands card has a band, release over value, of at least BAND_TAPS
    times the items one completion puts in its store. A chip's card takes the chip's own levels."""
    cards = {c.id: c for c in o.cards}
    for oc in o.order_cards:
        card = None if oc.tap_card is None else cards[oc.tap_card]
        if card is None or card.lane != HANDS or oc.chip is not None or oc.when.test != "at_most":
            continue
        yielded = sum(s.items for s in card.outcome.stores if s.store == oc.store)
        band = (oc.when.release or oc.when.value) - oc.when.value
        if yielded and band < BAND_TAPS * yielded:
            fail(f"order card for {oc.store}", f"its band is {band} items and {card.id} puts in {yielded} a completion: "
                 f"a hold covers fewer than {BAND_TAPS} completions, so the rule turns on and off at that rate")
