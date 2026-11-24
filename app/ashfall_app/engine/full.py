"""The full rule (DESIGN.txt, "FULL OUTPUT"): a fillable card whose every outcome store is full pauses, keeping its
inputs, and resumes once one of those stores falls to half its cap. A full pause is a Pause on a store its card makes.
"""
from dataclasses import replace

from .cards import CardDef
from .cardsides import card_makes, fillable, outcome_stores
from .counts import work_segment
from .gates import store_cap
from .ids import HANDS, CardId, StoreId
from .index import derived, index
from .installs import requeued
from .motion import store_segment
from .rates import exact_net, running, store_value, tapped_cards
from .rebuild import rebuild
from .rules import Rules
from .segments import reach_time
from .state import Pause, Save
from .work import interrupt


def is_full_pause(rules: Rules, pause: Pause) -> bool:
    """The Pause is on a store its card makes (a dry one is on a store it takes: one side per store, validation)."""
    card = index(rules).cards.get(CardId(pause.runner))
    return card is not None and pause.store in card_makes(card)


def resume_level(save: Save, rules: Rules, store: StoreId) -> int:
    """Half the store's cap now, rounded down: a full pause lifts once an outcome store is at or below it."""
    return store_cap(save, rules, store) // 2


def has_room(save: Save, rules: Rules, pause: Pause) -> bool:
    """Some outcome store of the full pause's card is at or below its resume level now."""
    return any(store_value(save, s) <= resume_level(save, rules, s) for s in _outcomes(rules, pause))


def resume_time(save: Save, rules: Rules, pause: Pause) -> int | None:
    """The first time an outcome store of the full pause's card falls to its resume level, on the current segments."""
    times = [save.time if store_value(save, s) <= (lvl := resume_level(save, rules, s))
             else reach_time(store_segment(save, rules, s), lvl) for s in _outcomes(rules, pause)]
    return min((t for t in times if t is not None), default=None)


def full_cards(save: Save, rules: Rules, landing: frozenset[CardId] = frozenset()) -> list[CardId]:
    """The full cards, in running order: fillable, holding no Pause, not landing at this instant, their work moving,
    and every outcome store at its cap with an exact net above 0."""
    cards = _fillable(rules)
    if not cards:
        return []
    now = running(save, rules)
    paused = {p.runner for p in save.pauses}
    found: list[CardId] = []
    for r in now.shares:
        c = cards.get(CardId(r))
        if c is None or c.id in paused or c.id in landing or work_segment(save, c.id).rate <= 0:
            continue
        if all(store_value(save, s) >= store_cap(save, rules, s) and exact_net(save, rules, now, s) > 0
               for s in outcome_stores(c)):
            found.append(c.id)
    return found


def pause_full(save: Save, rules: Rules, landing: frozenset[CardId]) -> tuple[Save, bool]:
    """Pause the full cards, last in running order first, re-reading after each, until none is full. A paused tapped
    card's tap ends at once (work.interrupt) and a hands tap goes back to the queue's front; the flag says whether one
    did."""
    interrupted = False
    while found := full_cards(save, rules, landing):
        card = index(rules).cards[found[-1]]
        first = outcome_stores(card)[0]
        pauses = save.pauses + (Pause(card.id, first, resume_level(save, rules, first)),)
        pos = index(rules).runner_pos
        save = rebuild(replace(save, pauses=tuple(sorted(pauses, key=lambda p: pos[p.runner]))), rules)
        lane = card.lane if card.id in tapped_cards(save, rules) else None
        if lane is not None:
            save, interrupted = interrupt(save, rules, lane), True
            if lane == HANDS:
                save = requeued(save, rules, card.id)
    return save, interrupted


def _outcomes(rules: Rules, pause: Pause) -> tuple[StoreId, ...]:
    return outcome_stores(index(rules).cards[CardId(pause.runner)])


def _fillable(rules: Rules) -> dict[CardId, CardDef]:
    return derived(rules, "_fillable_cards", lambda r: {c.id: c for c in r.cards if fillable(c)})
