"""Which cards make a store, read off the opening's own structure: what a short need names (Content's
StoreInfo.made_by). Pure; no rule lives here, only where each store comes from."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entries import CardEntry
    from .schema import Opening


def made_by(o: "Opening", store: str, index: "dict[str, list[str]] | None" = None) -> list[str]:
    """Card ids in card order: each card whose completion lands the store or whose make flow fills it; for a store no
    card makes that way, each card that trains a skill whose level pays the store, or whose completion count a find
    waits on (a trigger's stores). A one-off find beside a card that makes the store is no way to make more of it."""
    makers = card_makers(o, store, index)
    if makers:
        return makers
    finds = [t for t in o.triggers if any(a.store == store for a in t.outcome.stores) and t.when.id is not None]
    return [c.id for c in o.cards if any(
        (t.when.subject_kind == "skill_level" and t.when.id == c.skill)
        or (t.when.subject_kind == "card_count" and t.when.id == c.id) for t in finds)]


def card_makes(c: "CardEntry") -> list[str]:
    """The stores the card's completions land or its make flows fill (CardInfo.makes), each once, in content order."""
    return list(dict.fromkeys([*(a.store for a in [*c.outcome.stores, *c.finished.stores]), *(f.store for f in c.makes)]))


def card_takes(c: "CardEntry") -> list[str]:
    """The stores the card's inputs, costs and drains take from (CardInfo.takes), each once, in content order."""
    return list(dict.fromkeys([*(a.store for a in c.inputs), *(f.store for f in c.costs), *(a.store for a in c.drains)]))


def card_made(o: "Opening", store: str) -> bool:
    """Some card's completion lands the store or its make flow fills it."""
    return any(store in card_makes(c) for c in o.cards)


def makers_by_store(o: "Opening") -> dict[str, list[str]]:
    """card_makers of every store at once, for a caller that asks for many (`index` below)."""
    found: dict[str, list[str]] = {}
    for c in o.cards:
        for store in card_makes(c):
            found.setdefault(store, []).append(c.id)
    return found


def card_makers(o: "Opening", store: str, index: "dict[str, list[str]] | None" = None) -> list[str]:
    """Card ids in card order whose completion lands the store or whose make flow fills it: the cards a short need on
    it lights (View Need.makers). `index` is makers_by_store(o), passed when many stores are asked for."""
    if index is not None:
        return list(index.get(store, ()))
    return [c.id for c in o.cards if store in card_makes(c)]


def standing_makers(o: "Opening", store: str) -> list[str]:
    """Standing action ids in content order whose make flow fills the store."""
    return [a.id for a in o.standing if any(f.store == store for f in a.makes)]


def rises_in_steps(o: "Opening", store: str, index: "dict[str, list[str]] | None" = None) -> bool:
    """Nothing that runs raises the store: no card lands or flows it and no standing action flows it, so only an event
    (a lost fight, a find, an answer) adds to it, a step at a time (StoreInfo.rises_in_steps)."""
    return not card_makers(o, store, index) and not standing_makers(o, store)


def granted_by(o: "Opening", store: str) -> list[str]:
    """Trigger ids in content order whose outcome lands the store, each at a level a skill's row shows (up to the
    prestige top level) when it waits on one: where a store nothing makes comes from (View Need.gate)."""
    top = None if o.prestige is None else o.prestige.top_level
    return [t.id for t in o.triggers if any(a.store == store for a in t.outcome.stores)
            and not (t.when.subject_kind == "skill_level" and top is not None and t.when.value > top)]
