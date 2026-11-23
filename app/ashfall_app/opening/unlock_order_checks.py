"""What a locked store or standing action may not be shown to the player ahead of (a defect once opened a chip, covers
and rules about barley before any bed existed). A chip's effect, a card's stores, an order card's store and a standing
action's flows that name a store or action some outcome unlocks must themselves be unlocked only once that thing is: by
a trigger whose chain of waits (offer_caps.Chain) passes through an unlocker of it, or by a card `requires` on it.
Structural fields only. Raises ValueError naming the entry (refs.fail)."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .offer_caps import Chain
from .refs import fail

if TYPE_CHECKING:
    from .entries import ConditionEntry, ModifierEntry
    from .schema import Opening

Ref = tuple[str, str]
"""(unlock kind, id) of a store or standing action."""


def check_unlock_order(o: "Opening") -> None:
    for where, kind, id_, targets in unordered(o):
        fail(where, f"is unlocked ({kind} {id_}) before the {', '.join(f'{k} {i}' for k, i in targets)} it names, "
             "which something unlocks: gate it on that unlock")


def unordered(o: "Opening", chain: Chain | None = None) -> list[tuple[str, str, str, list[Ref]]]:
    """Each thing (where, unlock kind, id) that can be open while a thing it names is locked, with those things."""
    chain = chain or Chain(o)
    start = {(u.unlock_kind, u.id) for u in o.start}
    locked = {k for k in chain.unlocked_by if k[0] == "action"} - start
    locked |= {k for k in chain.unlocked_by if k[0] == "store" and k not in start and sealed(o, chain, k[1])}
    found: list[tuple[str, str, str, list[Ref]]] = []
    for where, kind, id_, names, required in _names(o):
        late = [k for k in names & locked if k not in required and not _after(chain, kind, id_, k)]
        if late:
            found.append((where, kind, id_, sorted(late)))
    return found


def sealed(o: "Opening", chain: Chain, store: str) -> bool:
    """Nothing can put `store` in the player's hands before it is unlocked: each way of making it (a card or standing
    action that makes it, an outcome that gives it) comes after one of its unlockers. A store the calendar unlocks is
    not sealed: its order against what the clock opens is the chapter's to place, and no chain of waits shows it."""
    gives = set(chain.unlockers("store", store))
    makers = [("card", c.id) for c in o.cards if any(f.store == store for f in c.makes)
              or any(a.store == store for a in (*c.outcome.stores, *c.finished.stores))]
    makers += [("action", a.id) for a in o.standing if any(f.store == store for f in a.makes)]
    placed = [w for w, out in chain.out.items() if any(a.store == store for a in out.stores)]
    scheduled = all(w in chain.triggers and chain.triggers[w].when.test == "after_time" for w in gives)
    return not scheduled and all(_after(chain, kind, id_, ("store", store)) for kind, id_ in makers) \
        and all(chain.before[w] & gives for w in placed)


def _after(chain: Chain, kind: str, id_: str, target: Ref) -> bool:
    """Every way `kind id_` is unlocked has an unlocker of `target` among what must have happened first."""
    ways = chain.unlockers(kind, id_)
    gives = set(chain.unlockers(*target))
    return bool(ways) and all(chain.before[w] & gives for w in ways)


def _names(o: "Opening") -> Iterator[tuple[str, str, str, set[Ref], set[Ref]]]:
    """(where, unlock kind, id, stores and actions it names, those its own requires wait on)."""
    for ch in o.chips:
        names = {k for m in ch.effects for k in _modified(m)}
        yield f"chip {ch.id}", "chip", ch.id, names, set()
    for c in o.cards:
        flows = [*c.inputs, *c.drains, *c.costs]
        yield f"card {c.id}", "card", c.id, {("store", f.store) for f in flows}, _required(c.requires)
    for a in o.standing:
        yield f"action {a.id}", "action", a.id, {("store", f.store) for f in a.costs}, set()
    for oc in o.order_cards:
        after = oc.offered_after
        kind, id_ = (after.unlock_kind, after.id) if after is not None else ("order", oc.store)
        yield f"order card for {oc.store} ({oc.tap_card or oc.switch_mix})", kind, id_, {("store", oc.store)}, set()


def _modified(m: "ModifierEntry") -> list[Ref]:
    out: list[Ref] = []
    if m.store:
        out.append(("store", m.store))
    if m.target == "rate":
        out.append(("action", m.id))
    return out


def _required(requires: "list[ConditionEntry]") -> set[Ref]:
    return {(c.unlock_kind, c.id) for c in requires
            if c.subject_kind == "unlocked" and c.test == "at_least" and c.unlock_kind and c.id}
