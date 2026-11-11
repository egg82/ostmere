"""Which cards make a store, read off the opening's own structure: what a short need names (Content's
StoreInfo.made_by). Pure; no rule lives here, only where each store comes from."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entries import CardEntry
    from .schema import Opening


def made_by(o: "Opening", store: str) -> list[str]:
    """Card ids in card order: each card whose completion lands the store or whose make flow fills it; for a store no
    card makes that way, each card that trains a skill whose level pays the store, or whose completion count a find
    waits on (a trigger's stores). A one-off find beside a card that makes the store is no way to make more of it."""
    makers = card_makers(o, store)
    if makers:
        return makers
    finds = [t for t in o.triggers if any(a.store == store for a in t.outcome.stores) and t.when.id is not None]
    return [c.id for c in o.cards if any(
        (t.when.subject_kind == "skill_level" and t.when.id == c.skill)
        or (t.when.subject_kind == "card_count" and t.when.id == c.id) for t in finds)]


def card_made(o: "Opening", store: str) -> bool:
    """Some card's completion lands the store or its make flow fills it."""
    return any(_makes(c, store) for c in o.cards)


def _makes(c: "CardEntry", store: str) -> bool:
    lumps = [*c.outcome.stores, *c.finished.stores]
    return any(a.store == store for a in lumps) or any(f.store == store for f in c.makes)


def card_makers(o: "Opening", store: str) -> list[str]:
    """Card ids in card order whose completion lands the store or whose make flow fills it: the cards a short need on
    it lights (View Need.makers)."""
    return [c.id for c in o.cards if _makes(c, store)]


def standing_makers(o: "Opening", store: str) -> list[str]:
    """Standing action ids in content order whose make flow fills the store."""
    return [a.id for a in o.standing if any(f.store == store for f in a.makes)]


def granted_by(o: "Opening", store: str) -> list[str]:
    """Trigger ids in content order whose outcome lands the store, each at a level a skill's row shows (up to the
    prestige top level) when it waits on one: where a store nothing makes comes from (View Need.gate)."""
    top = None if o.prestige is None else o.prestige.top_level
    return [t.id for t in o.triggers if any(a.store == store for a in t.outcome.stores)
            and not (t.when.subject_kind == "skill_level" and top is not None and t.when.value > top)]
