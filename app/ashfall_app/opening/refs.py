"""The lookups every Opening check shares (ids by kind, a reference that must be known, every outcome), and the
checks on references: each fraction exact, each condition, modifier and unlock naming something declared. Raises
ValueError naming the entry. Imports the schema for types only."""
from collections.abc import Iterator
from typing import TYPE_CHECKING, NoReturn

from ..engine import HANDS, QUANTITY_SCALE, per_hour, units
from .convert import amount, levels, note_trigger_id, offer_trigger_id

if TYPE_CHECKING:
    from .entries import ConditionEntry, FlowEntry, ItemAmount, ModifierEntry, OutcomeEntry, UnlockEntry
    from .schema import Opening


def fail(where: str, message: str) -> NoReturn:
    raise ValueError(f"{where}: {message}")


def ids_by_kind(o: "Opening") -> dict[str, list[str]]:
    return {
        "store": [s.id for s in o.stores], "skill": [s.id for s in o.skills], "action": [a.id for a in o.standing],
        "lane": [x.id for x in o.lanes], "card": [c.id for c in o.cards], "chip": [c.id for c in o.chips],
        "trigger": [t.id for t in o.triggers] + [offer_trigger_id(x.id) for x in o.offers]
        + [note_trigger_id(n.id) for n in o.notes],
        "feature": [f.id for f in o.features], "aim": [a.id for a in o.aims],
        "runner": [a.id for a in o.standing] + [c.id for c in o.cards],
        "side": [s.id for s in o.sides], "threat": [t.id for t in o.threats],
        "offer": [x.id for x in o.offers], "answer": [a.id for x in o.offers for a in x.answers],
        "entry": [e.id for e in o.entries], "note": [n.id for n in o.notes],
    }


def need(where: str, kind: str, id_: str, known: list[str]) -> None:
    if id_ not in known:
        fail(where, f"unknown {kind} {id_}")


# ---------- fractions ----------

def _amounts(o: "Opening") -> Iterator[tuple[str, "ItemAmount"]]:
    for c in o.cards:
        yield from ((f"card {c.id}", a) for a in (*c.inputs, *c.drains))
    for where, out in outcomes(o):
        yield from ((where, a) for a in out.stores)


def _flows(o: "Opening") -> Iterator[tuple[str, "FlowEntry"]]:
    for c in o.cards:
        yield from ((f"card {c.id}", f) for f in (*c.makes, *c.costs))
    for a in o.standing:
        yield from ((f"action {a.id}", f) for f in (*a.makes, *a.costs))


def _check_fractions(o: "Opening", ids: dict[str, list[str]]) -> None:
    stores = ids["store"]
    for where, a in _amounts(o):
        need(where, "store", a.store, stores)
        if (a.items * QUANTITY_SCALE) % a.every != 0:
            fail(where, f"{a.items} per {a.every} {a.store} does not divide exactly into quantity units")
    for where, f in _flows(o):
        if per_hour(f.items_per_hour) % f.every_hours != 0:
            fail(where, f"{f.items_per_hour} {f.store} per {f.every_hours} hours does not divide exactly into rate "
                        "units")


def _check_every(where: str, c: "ConditionEntry") -> None:
    """`every` divides a store's threshold only, value and release alike, each exactly."""
    if c.every == 1:
        return
    if c.test == "after_time" or c.subject_kind != "store":
        fail(where, "every divides a store's threshold only")
    release = c.value if c.release is None else c.release
    if units(c.value) % c.every != 0 or units(release) % c.every != 0:
        fail(where, f"{c.value} (release {release}) per {c.every} does not divide exactly into quantity units")


# ---------- conditions, modifiers, unlocks ----------

def outcomes(o: "Opening") -> Iterator[tuple[str, "OutcomeEntry"]]:
    for c in o.cards:
        yield f"card {c.id}", c.outcome
        yield f"card {c.id} finished", c.finished
    for t in o.triggers:
        yield f"trigger {t.id}", t.outcome
    for x in o.offers:
        yield from ((f"answer {a.id}", a.outcome) for a in x.answers)


def _conditions(o: "Opening") -> Iterator[tuple[str, "ConditionEntry", bool]]:
    """Every condition with where it sits, and whether it is a trigger's `when` or an offer's gate: the only places
    that may read lane_rules."""
    for c in o.cards:
        yield from ((f"card {c.id}", x, False) for x in c.requires)
    yield from ((f"chip {c.id}", c.when, False) for c in o.chips)
    for t in o.triggers:
        yield f"trigger {t.id}", t.when, True
        yield from ((f"trigger {t.id}", x, False) for x in t.requires)
    yield from ((f"order card for {c.store}", c.when, False) for c in o.order_cards)
    for x in o.offers:
        yield f"offer {x.id}", x.gate, True
        yield from ((f"offer {x.id}", c, False) for c in x.requires)
    for n in o.notes:
        yield f"note {n.id}", n.gate, True
        yield from ((f"note {n.id}", c, False) for c in n.requires)


def _modifiers(o: "Opening") -> Iterator[tuple[str, "ModifierEntry"]]:
    for c in o.chips:
        yield from ((f"chip {c.id}", m) for m in c.effects)
    for where, out in outcomes(o):
        yield from ((where, m) for m in out.modifiers)
    if o.camp is not None:
        for n, lv in enumerate(o.camp.levels, start=1):
            yield from ((f"camp level {n}", m) for m in lv.modifiers)


def offer_cap(o: "Opening", store: str, after: "UnlockEntry | None") -> float:
    """The cap `store` has for certain once `after` is unlocked, in items: its own cap with the cap modifiers that
    land with `after`, or with every outcome a trigger opening `after` counts up to. A rule offered then may let go
    above the store's first cap, never above this. Several ways to `after`: the least of them."""
    base = float(next(s.cap_items for s in o.stores if s.id == store))
    if after is None:
        return base
    ways = [_with(base, store, [*out.modifiers, *_counted(o, where)]) for where, out in outcomes(o)
            if any(u.unlock_kind == after.unlock_kind and u.id == after.id for u in out.unlocks)]
    return min(ways, default=base)


def _counted(o: "Opening", where: str) -> list["ModifierEntry"]:
    """A trigger waiting on a count of a store every one of whose makers it needs: those makers' modifiers."""
    t = next((t for t in o.triggers if where == f"trigger {t.id}"), None)
    if t is None or t.when.test != "at_least" or t.when.subject_kind != "store":
        return []
    makers = [out for _, out in outcomes(o) if any(a.store == t.when.id for a in out.stores)]
    if sum(amount(a).quantity for out in makers for a in out.stores if a.store == t.when.id) > levels(t.when)[0]:
        return []
    return [m for out in makers for m in out.modifiers]


def _with(base: float, store: str, mods: list["ModifierEntry"]) -> float:
    for m in mods:
        if m.target == "cap" and m.id == store:
            base = base * m.amount_bp / 10_000 if m.kind == "mul_bp" else base + m.amount_bp / 10_000
    return base


def _unlocks(o: "Opening") -> Iterator[tuple[str, "UnlockEntry"]]:
    yield from (("start", u) for u in o.start)
    for where, out in outcomes(o):
        yield from ((where, u) for u in out.unlocks)
    yield from ((f"order card for {c.store}", c.offered_after) for c in o.order_cards if c.offered_after is not None)
    yield from ((f"chip {c.id}", c.offered_after) for c in o.chips if c.offered_after is not None)
    yield from ((f"aim {a.id}", a.after) for a in o.aims if a.after is not None)
    yield from ((f"lane {x.id}", lb.after) for x in o.lanes for lb in x.later_labels)


def _unlock_ids(ids: dict[str, list[str]], unlock_kind: str) -> list[str]:
    """The ids an unlock of this kind may name: a retirement names a card, an answered unlock an offer, a joined or left one a lane."""
    named = {"retired": "card", "answered": "offer", "joined": "lane", "left": "lane"}
    return ids[named.get(unlock_kind, unlock_kind)]


def _check_lane_rules(o: "Opening", where: str, c: "ConditionEntry", is_gate: bool) -> None:
    """lane_rules: a trigger's `when` or an offer's gate, at_least, no release, on a ruled lane."""
    if not is_gate:
        fail(where, "lane_rules is only a trigger's when or an offer's gate")
    if c.test != "at_least" or c.release is not None:
        fail(where, "lane_rules takes at_least and no release")
    assert c.id is not None
    need(where, "ruled lane", c.id, [x.id for x in o.lanes if x.ruled])


def _check_condition(o: "Opening", ids: dict[str, list[str]], where: str, c: "ConditionEntry", is_gate: bool
                     ) -> None:
    _check_every(where, c)
    if c.test == "after_time":
        if any(x is not None for x in (c.subject_kind, c.id, c.unlock_kind, c.release)):
            fail(where, "after_time takes only a value")
        return
    if c.subject_kind is None or c.id is None:
        fail(where, f"{c.test} needs subject_kind and id")
    if (c.unlock_kind is not None) != (c.subject_kind == "unlocked"):
        fail(where, "unlock_kind goes with subject_kind unlocked, and only there")
    if c.subject_kind == "unlocked":
        assert c.unlock_kind is not None
        need(where, c.unlock_kind, c.id, _unlock_ids(ids, c.unlock_kind))
    elif c.subject_kind == "lane_rules":
        _check_lane_rules(o, where, c, is_gate)
    else:
        kind = {"store": "store", "skill_level": "skill", "card_count": "card", "running": "runner"}[c.subject_kind]
        need(where, kind, c.id, ids[kind])
    value, release = levels(c)
    if (c.test == "at_least" and release > value) or (c.test == "at_most" and release < value):
        fail(where, "release is on the wrong side of value")


def _check_modifier(ids: dict[str, list[str]], where: str, m: "ModifierEntry") -> None:
    if m.target == "rate":
        need(where, "runner", m.id, ids["runner"])
        if m.flow is None or (m.flow == "xp") != (m.store is None):
            fail(where, "a rate modifier needs a flow, and a store unless the flow is xp")
        if m.store is not None:
            need(where, "store", m.store, ids["store"])
        return
    if m.flow is not None or m.store is not None:
        fail(where, f"a {m.target} modifier takes no flow or store")
    if m.target == "work":
        need(where, "card", m.id, ids["card"])
    elif m.target == "cap":
        need(where, "store", m.id, ids["store"])
    elif m.target in ("side", "threat"):
        need(where, m.target, m.id, ids[m.target])
    else:
        need(where, "lane", m.id, [*ids["lane"], HANDS])


def check_refs(o: "Opening") -> None:
    """Every fraction exact and its store known; every condition, modifier and unlock names something known."""
    ids = ids_by_kind(o)
    _check_fractions(o, ids)
    for where, c, is_gate in _conditions(o):
        _check_condition(o, ids, where, c, is_gate)
    for where, m in _modifiers(o):
        _check_modifier(ids, where, m)
    for where, u in _unlocks(o):
        need(where, u.unlock_kind, u.id, _unlock_ids(ids, u.unlock_kind))
    holding = [a.id for a in o.standing if a.while_running]
    for c in o.cards:
        if c.upside_of is not None:
            need(f"card {c.id} upside_of", "standing action with while_running", c.upside_of, holding)
