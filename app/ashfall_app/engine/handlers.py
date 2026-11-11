"""What each event does to the save. Each handler re-checks its condition (a stale event is a no-op) and returns the
rebuilt save plus whether orders and the queue must evaluate (a latch or the queue changed, a tap landed or was
interrupted, a capped card completed, a trigger fired, a chip showed or hid, a READY fell). Kinds: events.EventKind.
"""
from collections.abc import Callable, Iterable
from dataclasses import replace

from .conditions import all_true, change_time, rise_time
from .counts import unit, work_segment, work_value
from .events import Event, EventKind
from .gates import is_unlocked, store_cap
from .ids import HANDS, CardId, LaneId, LineKey, Runner, StoreId
from .index import index
from .installs import requeued
from .lumps import drainers
from .phaseevents import carry_ended, topped_out
from .plan import controlling_entry
from .rates import FULL, contribution, lane_state, running, store_value, tapped_cards
from .rebuild import rebuild
from .requires import first_unmet
from .schedule import settled_entries
from .rules import Rules
from .state import Pause, Save
from .unlocks import Unlock, UnlockKind
from .units import SECONDS_PER_HOUR
from .work import apply_outcome, complete, first_shown, interrupt, land, ready, written_by

type Emit = Callable[[int, LineKey, CardId | None], None]
"""Where a handler sends the log lines it emits, as (engine time, key, the card that wrote it or None) in emission
order (DESIGN.txt, "Lines")."""


def ignore(time: int, key: LineKey, card: CardId | None) -> None:
    """The Emit of a caller that wants no lines."""


def handle(save: Save, rules: Rules, event: Event, emit: Emit = ignore,
           landing: frozenset[CardId] = frozenset()) -> tuple[Save, bool]:
    """COMPLETION: work.complete. TAP_DONE: work.land. REQUIRES: rebuild, a mix card starting or stopping WAITING, or
    work.interrupt for a tapped card. STORE_LIMIT: pauses as before, over runners, and work.interrupt when it pauses a
    tapped card; `landing` are the tapped cards whose landing is still to be handled at this instant, which the
    dry rule passes over. TOP_OUT, CARRY_END: phaseevents.py. RESUME, CHIP, TRIGGER, LATCH, QUEUE_POP, READY: as
    before the cards part. Afterwards a ready
    tap whose card no longer moves (its speed fell to 0) ends, interrupted."""
    after, changed = _dispatch(save, rules, event, emit, landing)
    return _stop_stalled(after, rules, changed)


def landing_cards(save: Save, rules: Rules, events: Iterable[Event]) -> frozenset[CardId]:
    """The tapped cards whose TAP_DONE is still to be handled at this instant: the landing stands, so the dry rule
    passes them over. A mix card's completion needs no such care: it counts by its work however the rule goes, so
    capped and uncapped cards stay alike."""
    ix = index(rules)
    found: set[CardId] = set()
    for e in events:
        if e.kind is EventKind.TAP_DONE:
            ls = lane_state(save, ix.lanes[e.sequence])
            if ls.card is not None and work_value(save, ls.card) > 0:
                found.add(ls.card)
    return frozenset(found)


def _stop_stalled(save: Save, rules: Rules, changed: bool) -> tuple[Save, bool]:
    """A tap holds the hands only while its card moves: one whose work rate is 0 ends, interrupted."""
    for ls in save.lanes:
        if ls.card is not None and ls.card in tapped_cards(save, rules) and work_segment(save, ls.card).rate <= 0:
            save, changed = interrupt(save, rules, ls.lane), True
    return save, changed


def _dispatch(save: Save, rules: Rules, event: Event, emit: Emit, landing: frozenset[CardId]) -> tuple[Save, bool]:
    if event.kind is EventKind.COMPLETION:
        return _completed(save, rules, CardId(event.subject), emit)
    if event.kind is EventKind.TAP_DONE:
        return _tap_done(save, rules, event.sequence, emit)
    if event.kind is EventKind.REQUIRES:
        return _requires_changed(save, rules, CardId(event.subject))
    if event.kind is EventKind.CHIP:
        after = _chip_changed(save, rules, event.sequence, emit)
        return after, after is not save
    if event.kind is EventKind.TRIGGER:
        return _trigger_fired(save, rules, event.sequence, emit)
    if event.kind is EventKind.STORE_LIMIT:
        return _pause_until_not_dry(save, rules, StoreId(event.subject), landing)
    if event.kind is EventKind.RESUME:
        return _resume(save, rules, event.subject), False
    if event.kind is EventKind.LATCH:
        i = event.sequence
        if change_time(save, rules, save.orders[i].when, save.latches[i]) != save.time:
            return save, False
        latches = save.latches[:i] + (not save.latches[i],) + save.latches[i + 1:]
        return replace(save, latches=latches), True
    if event.kind is EventKind.QUEUE_POP:
        settled = settled_entries(save, rules)
        if settled:
            # The controlling entry stays the first live one, so nothing new controls: no evaluation.
            return replace(save, queue=tuple(e for i, e in enumerate(save.queue) if i not in settled)), False
        head = controlling_entry(save, rules)
        if head is None or rise_time(save, rules, save.queue[head].until) != save.time:
            return save, False
        return replace(save, queue=save.queue[:head] + save.queue[head + 1:]), True
    if event.kind is EventKind.TOP_OUT:
        return topped_out(save, rules, event.sequence), False
    if event.kind is EventKind.CARRY_END:
        return carry_ended(save, rules, event.sequence), False
    return save, event.kind is EventKind.READY and (event.subject == "" or ready(save, rules, CardId(event.subject)))


def _dry(save: Save, store: StoreId) -> bool:
    seg = next(st.segment for st in save.stores if st.store == store)
    return seg.start_value == 0 and seg.rate < 0


def _pause_until_not_dry(save: Save, rules: Rules, store: StoreId, landing: frozenset[CardId]) -> tuple[Save, bool]:
    """Pause the store's consumers, last in running order first, until its net rate is >= 0, passing over a card in
    `landing` (it has finished) and the store's drains (forgiven at 0: rebuild holds the store there). A consumer reads
    its effective share, receivers of a paused card's share included; its resume level is an hour of its cost at its
    saved share, so nothing of a yield is written into a Pause (DESIGN.txt, "SPENT"). A paused tapped
    card ends its tap at once (work.interrupt); the flag says whether one did."""
    ix = index(rules)
    interrupted = False
    while _dry(save, store):
        now = running(save, rules)
        paused = {p.runner for p in save.pauses} | set(landing) | drainers(rules, store)
        consumers = [a for a in reversed(list(now.shares)) if a not in paused
                     and contribution(save, rules, a, store, now.shares[a], now.runs[a]) < 0]
        if not consumers:
            return save, interrupted
        a = consumers[0]
        saved = now.shares[a] - sum(g.share_bp for g in now.gained.get(a, ()))
        full_cost = -contribution(save, rules, a, store, saved, replace(FULL, speed=now.runs[a].speed))
        resume_at = min(store_cap(save, rules, store), full_cost * SECONDS_PER_HOUR)
        pauses = tuple(sorted(save.pauses + (Pause(a, store, resume_at),), key=lambda p: ix.runner_pos[p.runner]))
        save = rebuild(replace(save, pauses=pauses), rules)
        lane = _tapped_lane(save, rules, a)
        if lane is not None:
            save, interrupted = interrupt(save, rules, lane), True
            if lane == HANDS:
                save = requeued(save, rules, CardId(a))
    return save, interrupted


def _tapped_lane(save: Save, rules: Rules, runner: Runner) -> LaneId | None:
    """The lane a ready tap of `runner` occupies, or None."""
    card = CardId(runner)
    if card not in tapped_cards(save, rules):
        return None
    return next(ls.lane for ls in save.lanes if ls.card == card)


def _resume(save: Save, rules: Rules, runner: str) -> Save:
    pause = next((p for p in save.pauses if p.runner == runner), None)
    if pause is None or store_value(save, pause.store) < pause.resume_at:
        return save
    return rebuild(replace(save, pauses=tuple(p for p in save.pauses if p.runner != runner)), rules)


def _completed(save: Save, rules: Rules, card: CardId, emit: Emit) -> tuple[Save, bool]:
    """A capped card's work reached a completion: its line, outcome and, at the cap, finished. Orders and the queue
    evaluate after it."""
    c = index(rules).cards[card]
    if c.cap is None or work_value(save, card) < unit(c):
        return save, False
    own = written_by(c)
    save, lines = complete(save, rules, card)
    for key in lines:
        emit(save.time, key, card if key in own else None)
    return save, True


def _tap_done(save: Save, rules: Rules, lane_index: int, emit: Emit) -> tuple[Save, bool]:
    """A tap reached its completion. A lane freed meanwhile makes it stale."""
    ls = lane_state(save, index(rules).lanes[lane_index])
    if ls.card is None:
        return save, False
    if work_value(save, ls.card) == 0 or work_value(save, ls.card) % unit(index(rules).cards[ls.card]) != 0:
        return save, False
    save, lines = land(save, rules, ls.lane)
    for key in lines:
        emit(save.time, key, ls.card)
    return save, True


def _requires_changed(save: Save, rules: Rules, card: CardId) -> tuple[Save, bool]:
    """A card's requires changed truth: the rebuild starts or ends a mix card's WAITING; a tap whose requires now fail
    ends, interrupted."""
    save = rebuild(save, rules)
    lane = _tapped_lane(save, rules, card)
    if lane is None or first_unmet(save, rules, index(rules).cards[card]) is None:
        return save, False
    return interrupt(save, rules, lane), True


def _chip_changed(save: Save, rules: Rules, i: int, emit: Emit) -> Save:
    chip = rules.chips[i]
    if change_time(save, rules, chip.when, save.chips[i]) != save.time:
        return save
    on = not save.chips[i]
    save = rebuild(replace(save, chips=save.chips[:i] + (on,) + save.chips[i + 1:]), rules)
    if on:
        save, lines = first_shown(save, rules)
    else:
        lines = () if chip.off_line is None or not is_unlocked(save, rules, Unlock(UnlockKind.CHIP, chip.id)) \
            else (chip.off_line,)
    for line in lines:
        emit(save.time, line, None)
    return save


def _trigger_fired(save: Save, rules: Rules, i: int, emit: Emit) -> tuple[Save, bool]:
    """A trigger fires: orders and the queue evaluate after its outcome, as after a landing."""
    trigger = rules.triggers[i]
    if save.fired[i] or not all_true(save, rules, (trigger.when, *trigger.requires)):
        return save, False
    fired = save.fired[:i] + (True,) + save.fired[i + 1:]
    save, lines = apply_outcome(replace(save, fired=fired), rules, trigger.outcome)
    for key in lines:
        emit(save.time, key, None)
    return save, True
