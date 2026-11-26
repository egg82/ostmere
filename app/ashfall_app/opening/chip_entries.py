"""The status chip entries: a chip the camp shows, what it costs and when it is offered."""
from .entries import ConditionEntry, Entry, ModifierEntry, UnlockEntry


class ChipEntry(Entry):
    id: str
    label_key: str
    tone: str
    when: ConditionEntry
    effects: list[ModifierEntry] = []
    cost_key: str | None = None
    """What `effects` cost the player, in two or three words drawn with the chip; set exactly when it has effects."""
    on_line_key: str | None = None
    off_line_keys: list[str] = []
    """Said in turn each time the chip stops showing, one a time (engine ChipDef.off_lines); a pool of at least
    pool_checks.MIN_POOL lines, or none."""
    no_cure: bool = False
    """Shown with nothing the player can do about it, on purpose: the day-one gate that every chip shown has a cure
    (tests/dayone/cures.py) passes it over."""
    offered_after: UnlockEntry | None = None
    """Drawn on the page only once this is unlocked, as an order card's is offered: the chip's cure is on screen. The
    engine's latch is the same either way, so a chip with effects has none (its cost would run unseen); unlock such a
    chip with its cure instead."""
