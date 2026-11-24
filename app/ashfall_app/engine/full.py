"""The full rule (DESIGN.txt, "FULL OUTPUT"): a fillable card drawing a pool whose every outcome store is full pauses,
keeping its inputs, and resumes once one of those stores has room for a whole completion of it. A full pause is a Pause
on a store its card makes.
"""
from dataclasses import replace

from .cards import CardDef
from .cardsides import card_makes, fillable, outcome_stores
from .counts import work_segment
from .gates import store_cap
from .ids import CardId, StoreId
from .index import derived, index
from .motion import store_segment
from .lumps import lump_amount
from .modifiers import FlowKind, RateRef
from .rates import exact_net, running, store_value, tapped_cards
from .rebuild import rebuild
from .rules import Rules
from .segments import reach_time
from .spent import unmade
from .state import Pause, Save


def is_full_pause(rules: Rules, pause: Pause) -> bool:
    """The Pause is on a store its card makes (a dry one is on a store it takes: one side per store, validation)."""
    card = index(rules).cards.get(CardId(pause.runner))
    return card is not None and pause.store in card_makes(card)


def resume_level(save: Save, rules: Rules, card: CardDef, store: StoreId) -> int:
    """The store's cap now less one completion of the card's outcome on it: a full pause lifts once that much is room."""
    return max(0, store_cap(save, rules, store) - lump_amount(save, rules, card, RateRef(card.id, FlowKind.MAKE, store)))


def has_room(save: Save, rules: Rules, pause: Pause) -> bool:
    """Some outcome store of the full pause's card is at or below its resume level now."""
    card = _card(rules, pause)
    return any(store_value(save, s) <= resume_level(save, rules, card, s) for s in outcome_stores(card))


def resume_time(save: Save, rules: Rules, pause: Pause) -> int | None:
    """The first time an outcome store of the full pause's card falls to its resume level, on the current segments."""
    card = _card(rules, pause)
    times = [save.time if store_value(save, s) <= (lvl := resume_level(save, rules, card, s))
             else reach_time(store_segment(save, rules, s), lvl) for s in outcome_stores(card)]
    return min((t for t in times if t is not None), default=None)


def full_cards(save: Save, rules: Rules, landing: frozenset[CardId] = frozenset()) -> list[CardId]:
    """The full cards, in running order: fillable, drawing a pool (an input store no maker in play can make), holding no
    Pause, not landing at this instant, their work moving, and every outcome store at its cap with an exact net above 0.
    A tap is never full: it runs its one completion."""
    cards = _fillable(rules)
    if not cards:
        return []
    now = running(save, rules)
    paused = {p.runner for p in save.pauses} | set(tapped_cards(save, rules))
    found: list[CardId] = []
    for r in now.shares:
        c = cards.get(CardId(r))
        if c is None or c.id in paused or c.id in landing or work_segment(save, c.id).rate <= 0:
            continue
        if all(store_value(save, s) >= store_cap(save, rules, s) and exact_net(save, rules, now, s) > 0
               for s in outcome_stores(c)) and any(unmade(save, rules, a.store) for a in c.inputs):
            found.append(c.id)
    return found


def pause_full(save: Save, rules: Rules, landing: frozenset[CardId]) -> Save:
    """Pause the full cards, last in running order first, re-reading after each, until none is full."""
    while found := full_cards(save, rules, landing):
        card = index(rules).cards[found[-1]]
        first = outcome_stores(card)[0]
        pauses = save.pauses + (Pause(card.id, first, resume_level(save, rules, card, first)),)
        pos = index(rules).runner_pos
        save = rebuild(replace(save, pauses=tuple(sorted(pauses, key=lambda p: pos[p.runner]))), rules)
    return save


def _card(rules: Rules, pause: Pause) -> CardDef:
    return index(rules).cards[CardId(pause.runner)]


def _fillable(rules: Rules) -> dict[CardId, CardDef]:
    return derived(rules, "_fillable_cards", lambda r: {c.id: c for c in r.cards if fillable(c)})
