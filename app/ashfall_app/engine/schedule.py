"""Every event the current segments imply, at or after save.time. One at save.time is pending: it must be handled
before the instant is resolved. A resolved save has none pending.
"""
from .conditions import can_fall, change_time, is_true, rise_time
from .counts import unit, work_segment
from .events import Event, EventKind
from .ids import CardId
from .index import index
from .motion import store_segment
from .memo import SaveMemo
from .answers import AnswerKind, AnswerOffer
from .mixes import flatten_shares
from .offerstate import acting
from .orders import Condition, OrderVerb
from .phaseevents import phase_events
from .phases import next_level_xp
from .plan import candidates, controlling_entry, is_dead, live_queue_verb, mix_order
from .mixruns import running_mix, running_town_mix
from .rates import tapped_cards
from .retap import watch_events
from .rules import Rules
from .segments import reach_time
from .state import Save
from .triggers import trigger_events, triggers_now
from .work import blocker, tappable


_EVENTS: SaveMemo[tuple[Event, ...]] = SaveMemo()


def events(save: Save, rules: Rules) -> tuple[Event, ...]:
    """Every event of the save, built once per save: an instant asks again of the save it has not changed (a handler
    that changed nothing, an evaluation that applied no verb), and advance asks of the save the instant ended on."""
    return _EVENTS.get(save, rules, lambda: tuple(_events(save, rules)))


def _events(save: Save, rules: Rules) -> list[Event]:
    """STORE_LIMIT, RESUME (a paused runner's store refills), COMPLETION (each running capped card's next completion),
    TAP_DONE (a tapped card's next completion), LEVEL_UP, TOP_OUT and CARRY_END (phaseevents.py), REQUIRES (each running card's requires
    changing truth), CHIP, TRIGGER, LATCH (a CardCount solved off the work segment), QUEUE_POP, READY."""
    found = _store_events(save, rules) + _resume_events(save, rules) + _completion_events(save, rules)
    found += _tap_events(save, rules) + _level_events(save, rules) + phase_events(save, rules)
    found += _requires_events(save, rules)
    found += _chip_events(save, rules) + trigger_events(save, rules) + _ready_events(save, rules)
    found += watch_events(save, rules)
    for i, (order, latch) in enumerate(zip(save.orders, save.latches)):
        t = change_time(save, rules, order.when, latch)
        if t is not None:
            found.append(Event(t, EventKind.LATCH, i, str(i)))
    return found + _pop_events(save, rules)


def _pop_events(save: Save, rules: Rules) -> list[Event]:
    """The controlling entry's `until` rising, a dead entry's that cannot fall once it holds (it settles), and now for
    an entry answering an answered offer (it settles whatever its `until`)."""
    head = controlling_entry(save, rules)
    watched = [e.until for i, e in enumerate(save.queue)
               if i == head or (is_dead(save, rules, e.verb) and not can_fall(e.until))]
    times = [t for cond in watched if (t := rise_time(save, rules, cond)) is not None]
    times += [save.time] if any(_answered(save, rules, e.verb) for e in save.queue) else []
    return [Event(min(times), EventKind.QUEUE_POP, 0, "")] if times else []


def settled_entries(save: Save, rules: Rules) -> tuple[int, ...]:
    """The indices of dead queue entries whose `until` holds and cannot fall: a revival would pop them at once, so
    they pop now (DESIGN.txt, "Greyed mix"); and every entry answering an answered offer, dead for good, whatever its
    `until` (DESIGN.txt, "Dead")."""
    return tuple(i for i, e in enumerate(save.queue) if _answered(save, rules, e.verb) or (
        is_dead(save, rules, e.verb) and not can_fall(e.until) and is_true(save, rules, e.until)))


def _answered(save: Save, rules: Rules, verb: OrderVerb) -> bool:
    return isinstance(verb, AnswerOffer) and is_dead(save, rules, verb)


def pending(save: Save, rules: Rules) -> list[Event]:
    """The events at save.time, in events() order, equal to filtering events(). An instant asks after every handler,
    of saves it never asks the rest of, so the two kinds that cost most are found at now alone: a trigger on a level
    not yet reached, and a READY on any blocker but a pause, rise strictly later, because every segment starts at
    save.time (rebuild, shift) and reach_time from short of a target takes a second at least."""
    if _EVENTS.holds(save, rules):
        return [e for e in events(save, rules) if e.time == save.time]
    found = _store_events_now(save) + _resume_events(save, rules) + _completion_events(save, rules)
    found += _tap_events(save, rules) + _level_events(save, rules) + phase_events(save, rules)
    found += _requires_events(save, rules)
    found += _chip_events(save, rules) + triggers_now(save, rules) + _ready_now(save, rules)
    found += watch_events(save, rules)
    for i, (order, latch) in enumerate(zip(save.orders, save.latches)):
        if change_time(save, rules, order.when, latch) == save.time:
            found.append(Event(save.time, EventKind.LATCH, i, str(i)))
    return [e for e in found + _pop_events(save, rules) if e.time == save.time]



def _ready_now(save: Save, rules: Rules) -> list[Event]:
    """_ready_events at save.time: only a paused candidate's blocker can be ready now (a cascade's fall a second on)."""
    pos = index(rules).card_pos
    paused = {p.runner for p in save.pauses}
    found: list[Event] = []
    for card in candidates(save, rules):
        if card not in paused or not tappable(save, rules, card):
            continue
        b = blocker(save, rules, card)
        if b is not None and b.ready_at == save.time:
            found.append(Event(save.time, EventKind.READY, pos[card], card))
    return found


def _store_events(save: Save, rules: Rules) -> list[Event]:
    found: list[Event] = []
    for i, st in enumerate(save.stores):
        seg = store_segment(save, rules, st.store)
        if seg.start_value == 0 and seg.rate < 0:
            found.append(Event(save.time, EventKind.STORE_LIMIT, i, st.store))
        elif seg.limit is not None:
            t = reach_time(seg, seg.limit)
            if t is not None:
                found.append(Event(t, EventKind.STORE_LIMIT, i, st.store))
    return found


def _store_events_now(save: Save) -> list[Event]:
    """_store_events at save.time, read off the save's own segments: a store reaches its limit now only by standing
    on it, as reach_time from anywhere else takes a second at least."""
    return [Event(save.time, EventKind.STORE_LIMIT, i, st.store) for i, st in enumerate(save.stores)
            if (st.segment.start_value == 0 and st.segment.rate < 0) or st.segment.start_value == st.segment.limit]


def _resume_events(save: Save, rules: Rules) -> list[Event]:
    found: list[Event] = []
    pos = index(rules).runner_pos
    for p in save.pauses:
        seg = store_segment(save, rules, p.store)
        t = save.time if seg.start_value >= p.resume_at else reach_time(seg, p.resume_at)
        if t is not None:
            found.append(Event(t, EventKind.RESUME, pos[p.runner], p.runner))
    return found


def _completion_events(save: Save, rules: Rules) -> list[Event]:
    """A running capped card's work first reaches its next completion, solved off the segment as a latch is."""
    ix = index(rules)
    found: list[Event] = []
    for cs in save.cards:   # a card with no state has no work rising
        c = ix.cards.get(cs.card)
        seg = cs.work
        if c is not None and c.cap is not None and seg.rate > 0:
            t = reach_time(seg, (seg.start_value // unit(c) + 1) * unit(c))
            if t is not None:
                found.append(Event(t, EventKind.COMPLETION, ix.card_pos[c.id], c.id))
    return sorted(found, key=lambda e: e.sequence)


def _tap_events(save: Save, rules: Rules) -> list[Event]:
    found: list[Event] = []
    tapped = set(tapped_cards(save, rules))
    for i, ls in enumerate(save.lanes):
        if ls.card is None:
            continue
        seg = work_segment(save, ls.card) if ls.card in tapped else None
        t = None if seg is None or seg.limit is None else reach_time(seg, seg.limit)
        if t is not None:
            found.append(Event(t, EventKind.TAP_DONE, i, ls.lane))
    return found


def _level_events(save: Save, rules: Rules) -> list[Event]:
    found: list[Event] = []
    for i, st in enumerate(save.skills):
        nxt = next_level_xp(rules.curve, rules.prestige, st.phase.phase, st.xp.start_value)
        t = reach_time(st.xp, nxt) if nxt is not None else None
        if t is not None:
            found.append(Event(t, EventKind.LEVEL_UP, i, st.skill))
    return found


def _requires_events(save: Save, rules: Rules) -> list[Event]:
    """For each card a mix holds or a tap runs that has requires: the first time one of them changes truth."""
    watched: set[CardId] = {s.card for m in (running_mix(save, rules), running_town_mix(save, rules)) if m is not None
                            for s in flatten_shares(save.mixes, m.id)}
    watched |= set(tapped_cards(save, rules))
    found: list[Event] = []
    for i, c in enumerate(rules.cards):
        if c.id not in watched:
            continue
        times = [t for cond in c.requires if (t := _truth_change(save, rules, cond)) is not None]
        if times:
            found.append(Event(min(times), EventKind.REQUIRES, i, c.id))
    return found


def _truth_change(save: Save, rules: Rules, cond: Condition) -> int | None:
    """When a requires condition next changes truth. It is read as a plain threshold, with no hysteresis band."""
    return change_time(save, rules, cond, is_true(save, rules, cond))


def _chip_events(save: Save, rules: Rules) -> list[Event]:
    found: list[Event] = []
    for i, (chip, latch) in enumerate(zip(rules.chips, save.chips)):
        t = change_time(save, rules, chip.when, latch)
        if t is not None:
            found.append(Event(t, EventKind.CHIP, i, chip.id))
    return found


def _ready_events(save: Save, rules: Rules) -> list[Event]:
    """A card a true order or the controlling queue entry would tap turns ready (later than now) while it could be
    tapped; and, when the firing cap suspended evaluation at this instant, one second on for every such card already
    ready, and one more for the verbs with no card that could act, so the hands never idle on the cap (DESIGN.txt,
    "Evaluation after a cascade", both entries)."""
    found: list[Event] = []
    pos = index(rules).card_pos
    cascaded = save.last_cascade is not None and save.last_cascade.time == save.time
    if cascaded and _cardless_waits(save, rules):
        found.append(Event(save.time + 1, EventKind.READY, len(rules.cards), ""))
    for card in candidates(save, rules):
        if not tappable(save, rules, card):
            continue
        b = blocker(save, rules, card)
        if b is None and cascaded:
            found.append(Event(save.time + 1, EventKind.READY, pos[card], card))
        elif b is not None and b.ready_at is not None:
            found.append(Event(b.ready_at, EventKind.READY, pos[card], card))
    return found


def _cardless_waits(save: Save, rules: Rules) -> bool:
    """A verb with no card could act: a true order's AnswerOffer or AnswerKind that can act, or, while no order's mix
    runs, a controlling queue entry's AnswerOffer that can act."""
    if any(latch and isinstance(o.then, (AnswerOffer, AnswerKind)) and acting(save, rules, o.then) is not None
           for o, latch in zip(save.orders, save.latches)):
        return True
    queued = live_queue_verb(save, rules) if mix_order(save, rules) is None else None
    return isinstance(queued, AnswerOffer) and acting(save, rules, queued) is not None
