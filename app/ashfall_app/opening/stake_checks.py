"""A card that takes stores gives the player something they can see (docs/decisions/pacing.md, "A sink shows what it
buys"). An uncapped card that takes stores and gives nothing by itself, clears no chip and is read by no condition past
its first completion is a bare sink: it declares its `stake`, what it feeds, and its face says it (upside_key); the
whole content bears the stake out. Ids and fields only, never text. Raises ValueError naming the cards (refs.fail)."""
from typing import TYPE_CHECKING

from .fight_refs import fights
from .refs import conditions, fail

if TYPE_CHECKING:
    from .entries import CardEntry, OutcomeEntry
    from .schema import Opening


def check_stakes(o: "Opening") -> None:
    """Every bare sink declares its stake and has an upside_key; a stake sits only on a bare sink. Holds of each
    chapter's state, since the stake is declared where the card is."""
    missing = [c.id for c in o.cards if c.stake is None and bare(o, c)]
    if missing:
        fail(f"cards {', '.join(missing)}", "take stores and give nothing: each declares its stake (what it feeds) and "
                                            "says it with an upside_key")
    for c in o.cards:
        if c.stake is not None and not bare(o, c):
            fail(f"card {c.id}", "has a stake but gives something by itself, clears a chip or is read past its first "
                                 "completion")
        if c.stake is not None and c.upside_key is None:
            fail(f"card {c.id}", "has a stake and no upside_key, so its face does not say what it feeds")


def check_stakes_hold(o: "Opening") -> None:
    """A "side" stake: once any fight exists, the card holds an entry on a side some fight is fought on (its
    while_running, which a later chapter may add)."""
    fought = {f.side for _, f in fights(o)}
    if not fought:
        return
    for c in o.cards:
        if c.stake == "side" and not any(w.side in fought for w in c.while_running):
            fail(f"card {c.id}", "has the stake side but holds no entry on a side any fight is fought on")


def bare(o: "Opening", c: "CardEntry") -> bool:
    """Uncapped, takes stores, and gives nothing by itself: no make, nothing in its outcome or finish, no fight, no
    chip's store taken, and no condition reading it running or past its first completion."""
    takes = {a.store for a in (*c.inputs, *c.drains)} | {f.store for f in c.costs}
    gives = bool(c.makes) or _gives(c.outcome) or _gives(c.finished) or c.fight is not None
    chips = {ch.when.id for ch in o.chips if ch.when.subject_kind == "store"}
    read = any(x.id == c.id and (x.subject_kind == "running" or (x.subject_kind == "card_count" and x.value > 1))
               for _, x, _ in conditions(o))
    return c.cap is None and bool(takes) and not gives and not takes & chips and not read


def _gives(out: "OutcomeEntry") -> bool:
    return any((out.stores, out.unlocks, out.modifiers, out.raises, out.starts, out.line_keys, out.orders, out.queues,
                out.joins, out.retire_orders, out.leaves))
