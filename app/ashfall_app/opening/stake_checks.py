"""A card that takes stores gives the player something they can see (docs/decisions/pacing.md, "A sink shows what it
buys"). An uncapped card that takes stores and gives nothing by itself, cures nothing and is read by no condition past
its first completion is a bare sink: it declares its `stake`, what it feeds, and its face says it (upside_key); the
whole content bears the stake out. Ids and fields only, never text. Raises ValueError naming the cards (refs.fail)."""
from typing import TYPE_CHECKING

from .convert import levels
from .fight_refs import fights
from .refs import conditions, fail

if TYPE_CHECKING:
    from .entries import CardEntry, ModifierEntry, OutcomeEntry, TriggerEntry
    from .schema import Opening


def check_stakes(o: "Opening") -> None:
    """Every bare sink declares its stake, and every stake has an upside_key. Holds of each chapter's state, since the
    stake is declared where the card is."""
    sinks = bare(o)
    missing = [c.id for c in o.cards if c.stake is None and c.id in sinks]
    if missing:
        fail(f"cards {', '.join(missing)}", "take stores and give nothing: each declares its stake (what it feeds) and "
                                            "says it with an upside_key")
    for c in o.cards:
        if c.stake is not None and c.upside_key is None:
            fail(f"card {c.id}", "has a stake and no upside_key, so its face does not say what it feeds")
    silent = [c.id for c in o.cards if c.presentation != "narrative" and c.inputs and c.upside_key is None and not _shows_gain(c)]
    if silent:
        fail(f"cards {', '.join(silent)}", "take stores and show nothing gained on their face: each says what it is for "
                                           "with an upside_key (decisions.md, \"Every option offered works as worded\")")


def _shows_gain(c: "CardEntry") -> bool:
    """The card's face or ledger shows what it gives: stores or modifiers it pays, a flow, a drain, XP, a held entry."""
    paid = (c.outcome.stores, c.outcome.modifiers, c.finished.stores, c.finished.modifiers)
    return any(paid) or bool(c.makes or c.drains or c.skill or c.while_running)


def check_stakes_hold(o: "Opening") -> None:
    """A "side" stake: once any fight exists, the card holds an entry on a side some fight is fought on (its
    while_running, which a later chapter may add). A "reach" stake: some trigger on a store the card's completions fill
    pays a modifier (reach_modifiers)."""
    for c in o.cards:
        if c.stake == "reach" and not reach_modifiers(o, c):
            fail(f"card {c.id}", "has the stake reach but no trigger on a store it fills pays a modifier")
        if c.stake == "speed" and not any(w.lane is not None for w in c.while_running):
            fail(f"card {c.id}", "has the stake speed but holds no lane's speed while it runs")
    fought = {f.side for _, f in fights(o)}
    if not fought:
        return
    for c in o.cards:
        if c.stake == "side" and not any(w.side in fought for w in c.while_running):
            fail(f"card {c.id}", "has the stake side but holds no entry on a side any fight is fought on")


def _reach_triggers(o: "Opening", c: "CardEntry") -> list["TriggerEntry"]:
    filled = {s.store for s in c.outcome.stores}
    return [t for t in o.triggers if t.when.test == "at_least" and t.when.subject_kind == "store"
            and t.when.id in filled and t.outcome.modifiers]


def reach_modifiers(o: "Opening", c: "CardEntry") -> list["ModifierEntry"]:
    """What a reach buys: the modifiers of the triggers on an at_least of a store the card's completions fill, in
    trigger order."""
    return [m for t in _reach_triggers(o, c) for m in t.outcome.modifiers]


def reach_stops(o: "Opening", c: "CardEntry") -> list[tuple[str, int]]:
    """Each reach of a card with the stake reach: (the store it reads, its threshold in quantity units), in trigger
    order. The face draws the store against the next of these (CardInfo.reach)."""
    return [(str(t.when.id), levels(t.when)[0]) for t in _reach_triggers(o, c)]


def bare(o: "Opening") -> set[str]:
    """The bare sinks: uncapped cards that take stores and give nothing by themselves (no make, nothing in the outcome
    or finish, no fight), take no bad store (one a chip reads or a fight wounds into: a cure), and are read by no
    condition running or past their first completion."""
    bad = {ch.when.id for ch in o.chips if ch.when.subject_kind == "store"} | {a.store for _, f in fights(o) for a in f.wounds}
    read = {x.id for _, x, _ in conditions(o) if x.subject_kind == "running" or (x.subject_kind == "card_count" and x.value > 1)}
    return {c.id for c in o.cards if c.cap is None and c.id not in read and _takes(c) and not _takes(c) & bad
            and not (c.makes or _gives(c.outcome) or _gives(c.finished) or c.fight is not None)}


def _takes(c: "CardEntry") -> set[str]:
    return {a.store for a in (*c.inputs, *c.drains)} | {f.store for f in c.costs}


def _gives(out: "OutcomeEntry") -> bool:
    return any((out.stores, out.unlocks, out.modifiers, out.raises, out.starts, out.line_keys, out.orders, out.queues,
                out.joins, out.retire_orders, out.leaves))
