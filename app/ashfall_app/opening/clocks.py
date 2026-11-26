"""Moment clocks: a hidden count-up store, in twentieths of a game hour, that the scene reads as a window
(`store:<id>@<a>..<b>`, tools/scene/people_moments.py) on a moment. A moment is authored as `clock = "<id>"` on an outcome,
which starts it, or on a `[line_doings.<key>]` entry, which starts it when the line is told: the loader then makes the
store, the standing action that counts it and, for a line, the trigger that unlocks the action. That trigger's `when`
and `requires` are the owner's own (the offer's gate and requires; for a card, its completion number for the line),
so the window follows the owner whatever is edited."""
from typing import TYPE_CHECKING

from .entries import ConditionEntry, FlowEntry, OutcomeEntry, StandingEntry, TriggerEntry, UnlockEntry
from .refs import fail
from .store_entries import StoreEntry

if TYPE_CHECKING:
    from .schema import Opening

PER_HOUR = 20
CAP_ITEMS = 400
STORE_LABEL, ACTION_LABEL = "store_moment_clock", "action_moment_clock"


def _outcome_clocks(o: "Opening") -> list[str]:
    owners = [t.outcome for t in o.triggers] + [x for c in o.cards for x in (c.outcome, c.finished)]
    owners += [a.outcome for x in o.offers for a in x.answers]
    return [x.clock for x in owners if x.clock is not None]


def clock_ids(o: "Opening") -> list[str]:
    """Every moment clock the content marks, outcomes' first, in content order."""
    return [*_outcome_clocks(o), *(e.clock for e in o.line_doings.values() if e.clock is not None)]


def _owner(o: "Opening", key: str) -> tuple[ConditionEntry, list[ConditionEntry]]:
    """When the line is told: the offer's own gate and requires, or the card's completion that says it (a told step's line
    k is said at completion k, engine DESIGN.txt)."""
    cards, offers = [c for c in o.cards if key in c.line_keys], [x for x in o.offers if key in x.line_keys]
    if len(cards) + len(offers) != 1:
        fail(f"line_doings {key}", f"has a clock and is told by {len(cards)} cards and {len(offers)} offers, not exactly one")
    if cards:
        card = cards[0]
        return ConditionEntry(test="at_least", subject_kind="card_count", id=card.id, value=card.line_keys.index(key) + 1), []
    return offers[0].gate, offers[0].requires


def with_moment_clocks(o: "Opening") -> "Opening":
    """`o` with the store, standing action and unlock of each marked clock. A clock already expanded (the shipped content
    merged on again with a test chapter) is left alone; a store of that id that is not the clock's own fails."""
    ids = clock_ids(o)
    if len(set(ids)) != len(ids):
        fail("clock", f"is marked twice: {sorted({i for i in ids if ids.count(i) > 1})}")
    if not ids:
        return o
    have = {s.id: s for s in o.stores}
    made = {i: StoreEntry(id=i, label_key=STORE_LABEL, cap_items=CAP_ITEMS, hidden=True) for i in ids}
    for i, store in made.items():
        if i in have and have[i] != store:
            fail(f"clock {i}", "is the id of a store that is not a moment clock")
    new = [i for i in ids if i not in have]

    def start(i: str) -> UnlockEntry:
        return UnlockEntry(unlock_kind="action", id=i)

    def out(x: OutcomeEntry) -> OutcomeEntry:
        if x.clock is None or x.clock not in new:
            return x
        return x.model_copy(update={"unlocks": [*x.unlocks, start(x.clock)]})

    lines = [(key, e.clock) for key, e in o.line_doings.items() if e.clock in new]
    triggers: list[TriggerEntry] = []
    for key, clock in lines:
        when, requires = _owner(o, key)
        triggers.append(TriggerEntry(id=f"t_{clock}", when=when, requires=requires,
                                     outcome=OutcomeEntry(unlocks=[start(str(clock))])))
    return o.model_copy(update={
        "stores": [*o.stores, *(made[i] for i in new)],
        "standing": [*o.standing, *(StandingEntry(id=i, label_key=ACTION_LABEL, makes=[FlowEntry(store=i, items_per_hour=PER_HOUR)])
                                    for i in new)],
        "triggers": [*(t.model_copy(update={"outcome": out(t.outcome)}) for t in o.triggers), *triggers],
        "cards": [c.model_copy(update={"outcome": out(c.outcome), "finished": out(c.finished)}) for c in o.cards],
        "offers": [x.model_copy(update={"answers": [a.model_copy(update={"outcome": out(a.outcome)}) for a in x.answers]})
                   for x in o.offers],
    })
