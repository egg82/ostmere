"""A store line's prefilled rule as the content writes it (opening.toml's and the chapters' order_cards)."""
from .entries import ConditionEntry, Entry, UnlockEntry


class OrderCardEntry(Entry):
    """The prefilled rule for a store's line: `when` an at_most on that store, offered under its falling line, or an
    at_least, offered under its full or rising line while the card it taps (one that takes that store) is idle; the
    page words it from ui text. then: a card to tap, or a mix to switch to."""

    store: str
    when: ConditionEntry
    tap_card: str | None = None
    switch_mix: str | None = None
    offered_after: UnlockEntry | None = None
    """Offered only once this is unlocked: the drain the order answers has begun (a line falling for a moment before
    then, a roast drawing roots, gets no order card)."""
    chip: str | None = None
    """The chip this card answers: offered in the hands strip while that chip shows, not under a ledger line, and
    `when` is that chip's own (the rule reads as the chip)."""
    after_end: bool = False
    """Offered only after the end, once its lines have been read: a step taught past the opening. Needs `chip`."""
