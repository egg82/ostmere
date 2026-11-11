"""Repeating taps: a lane whose rules would start the same card again at each of its completions runs that card as a
rate, its work with no limit, so its completions cost no instant (DESIGN.txt, part "REPEATING TAPS").

The settle, run at the end of every instant, decides which taps repeat; the watch events mark the one change of a
lane's task that nothing else would (an earlier rule's card turning ready while the lane is busy)."""
from dataclasses import replace

from .cards import CardDef
from .counts import is_completed, repeating, unit, work_segment
from .decisions import holds
from .events import Event, EventKind
from .gates import is_unlocked
from .ids import HANDS, CardId, LaneId
from .index import index
from .lanes import TapCard
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind
from .work import blocker, land

def may_repeat(card: CardDef) -> bool:
    """A card whose landing does nothing a rate would miss: uncapped (no COMPLETION), no inputs or drains (no
    threshold read at each landing), no tap line, and off the hands (a landing there lets the mix run for the
    instant)."""
    return card.lane != HANDS and card.cap is None and not card.inputs and not card.drains and not card.lines


def crossing(save: Save, rules: Rules) -> frozenset[LaneId]:
    """The lanes whose tap repeats into this instant with its work standing exactly on a completion: the per-landing
    engine had a landing here, so a task change at this instant lands them now."""
    found: set[LaneId] = set()
    for ls in save.lanes:
        if ls.card is not None and repeating(save, rules, ls.card):
            w = work_segment(save, ls.card).start_value
            if w > 0 and w % unit(index(rules).cards[ls.card]) == 0:
                found.add(ls.lane)
    return frozenset(found)


def settle(save: Save, rules: Rules, crossing: frozenset[LaneId]) -> tuple[Save, bool]:
    """One step of the settle: first a repeating tap whose task no longer holds is bounded at its next completion (or,
    on a lane in `crossing`, lands now: the returned flag, after which orders and the queue evaluate); only when none
    is left does a bounded tap whose task holds lose its limit. Returns the save it was given when nothing changes."""
    taps = _taps(save, rules)
    task = {lane: holds(save, rules, lane, card) for lane, card in taps}
    for lane, card in taps:
        if repeating(save, rules, card) and not task[lane]:
            return _stop(save, rules, lane, card, lane in crossing)
    for lane, card in taps:
        if not repeating(save, rules, card) and task[lane]:
            return _limited(save, card, None), False
    return save, False


def _taps(save: Save, rules: Rules) -> list[tuple[LaneId, CardId]]:
    """The running taps that may repeat (a stalled one is interrupted by the handlers, never repeated)."""
    cards = index(rules).cards
    return [(ls.lane, ls.card) for ls in save.lanes if ls.card is not None and may_repeat(cards[ls.card])
            and work_segment(save, ls.card).rate > 0]


def _stop(save: Save, rules: Rules, lane: LaneId, card: CardId, now: bool) -> tuple[Save, bool]:
    """Bound the tap at its next completion, or land it now (a card that may repeat has no tap line to say)."""
    if now:
        return land(save, rules, lane)[0], True
    whole = unit(index(rules).cards[card])
    return _limited(save, card, (work_segment(save, card).start_value // whole + 1) * whole), False


def _limited(save: Save, card: CardId, limit: int | None) -> Save:
    return replace(save, cards=tuple(replace(cs, work=replace(cs.work, limit=limit)) if cs.card == card else cs
                                     for cs in save.cards))


def watch_events(save: Save, rules: Rules) -> list[Event]:
    """While a lane repeats, a READY at the ready_at of each card a true order earlier than the first one tapping the
    lane's card would tap on that lane, unlocked, not completed and blocked (DESIGN.txt, "What can end a task")."""
    found: list[Event] = []
    ix = index(rules)
    for ls in save.lanes:
        if ls.card is None or not repeating(save, rules, ls.card):
            continue
        for order, latch in zip(save.orders, save.latches):
            verb = order.then
            if not latch or not isinstance(verb, TapCard):
                continue
            if verb.card == ls.card:
                break
            c = ix.cards.get(verb.card)
            if c is None or c.lane != ls.lane or is_completed(save, rules, c.id) \
                    or not is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id)):
                continue
            b = blocker(save, rules, c.id)
            if b is not None and b.ready_at is not None:
                found.append(Event(b.ready_at, EventKind.READY, ix.card_pos[c.id], c.id))
    return found
