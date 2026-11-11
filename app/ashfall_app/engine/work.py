"""What cards, chips, triggers and unlocks do to a save. Semantics: DESIGN.txt, part "CARDS", and "Chips" through
"Unlocks".

Every function returns a rebuilt save (rates recomputed at save.time) or reads only.
"""
from dataclasses import replace

from . import counts, discrete, gates
from .cards import Blocker, CapRaise, CardDef, CardState, LaneState, Outcome
from .conditions import is_true, rise_time
from .errors import InvalidVerbError
from .gates import shown_chips, store_cap, tap_speed
from .ids import HANDS, CardId, LaneId, LineKey, MixId, StoreId
from .index import index
from .installs import installed, queued, without_taps
from .joins import joined
from .leaves import left, present_installs
from .plan import candidates
from .lanes import TapCard
from .inputs import input_rest
from .modifiers import Modifier, RunKind
from .orders import AtLeast, Condition, DiscreteSubject, StoreValue
from .rates import FULL, lane_state, running, store_value, work_line
from .rebuild import rebuild
from .rules import Rules
from .segments import Segment
from .state import Save, StoreState
from .unlocks import Unlock, UnlockKind, unlock_key
from .units import BP, ceil_div


def blocker(save: Save, rules: Rules, card: CardId) -> Blocker | None:
    """None when a tap of `card` now would start ready; else its first unmet precondition, with the time every unmet
    one holds (cards.Blocker). Reading: never changes the save."""
    unmet = unmet_conditions(save, rules, card)
    if not unmet:
        return None
    times = [rise_time(save, rules, cond) for cond in unmet]
    return Blocker(unmet[0], None if None in times else max(t for t in times if t is not None))


def unmet_conditions(save: Save, rules: Rules, card: CardId) -> tuple[Condition, ...]:
    """What a tap of `card` now still lacks: each input's rest in declaration order, then each drain's store above 0,
    then each requires, then a pause."""
    c = index(rules).cards[card]
    found: list[Condition] = [AtLeast(StoreValue(store), q, q)
                              for store, q in input_rest(save, rules, c) if store_value(save, store) < q]
    found += [AtLeast(StoreValue(a.store), 1, 1) for a in c.drains if store_value(save, a.store) < 1]
    found += [cond for cond in c.requires if not is_true(save, rules, cond)]
    pause = next((p for p in save.pauses if p.runner == card), None)
    if pause is not None:
        found.append(AtLeast(StoreValue(pause.store), pause.resume_at, pause.resume_at))
    return tuple(found)


def tappable(save: Save, rules: Rules, card: CardId) -> bool:
    """The card is known, unlocked, not completed, and its lane is free: a tap would not be refused."""
    return _refusal(save, rules, card) is None


def ready(save: Save, rules: Rules, card: CardId) -> bool:
    """A tap now by an order or the queue would begin a ready completion: tappable and no blocker."""
    return tappable(save, rules, card) and blocker(save, rules, card) is None


def tap_seconds(save: Save, rules: Rules, card: CardId) -> int | None:
    """Seconds a tap started now takes: the rest of the current completion's work at the current full-share speed;
    None when that speed is 0, and then a tap is refused (InvalidVerbError from the player, nothing from an order)."""
    c = index(rules).cards[card]
    speed = work_line(save, rules, card, BP, FULL).per_hour
    if speed <= 0:
        return None
    return ceil_div(counts.unit(c) - counts.work_value(save, card) % counts.unit(c), speed)


def tap(save: Save, rules: Rules, verb: TapCard, by_player: bool) -> Save:
    """The save after tapping verb.card at save.time. by_player: locked, unknown, completed, a busy lane or a speed of
    0 raises InvalidVerbError. Otherwise an order, the queue or an Outcome: any of those changes nothing. An unready
    card changes nothing either (from the player it is a failed tap, whose line api.decide emits: DESIGN.txt, "Failed
    tap"). A ready tap takes nothing at its start: it runs the card at a full share from its current work to the next
    completion, every line (inputs and outcome stores included) at that share (DESIGN.txt, "One bar"). A fresh tap is
    bounded at that completion; only retap.settle lets it repeat (DESIGN.txt, "REPEATING TAPS")."""
    refusal = _refusal(save, rules, verb.card)
    if refusal is None and tap_seconds(save, rules, verb.card) is None:
        refusal = f"card {verb.card} cannot run: its speed is 0"
    if refusal is not None:
        if by_player:
            raise InvalidVerbError(refusal)
        return save
    if blocker(save, rules, verb.card) is not None:
        return save
    lane = index(rules).cards[verb.card].lane
    speed = tap_speed(save, rules, verb.card) if lane == HANDS else None
    occupied = tuple(LaneState(lane, verb.card, speed) if ls.lane == lane else ls for ls in save.lanes)
    stilled = tuple(replace(cs, work=Segment(save.time, cs.work.start_value, 0)) if cs.card == verb.card else cs
                    for cs in save.cards)
    return rebuild(replace(save, lanes=occupied, cards=stilled), rules)


def land(save: Save, rules: Rules, lane: LaneId) -> tuple[Save, tuple[LineKey, ...]]:
    """The TAP_DONE handler: the tapped card's work reached its next completion (a capped card's COMPLETION has
    already resolved at this instant). Frees the lane (the mix's yield ends) and returns an uncapped card's tap line."""
    ls = lane_state(save, lane)
    assert ls.card is not None
    c = index(rules).cards[ls.card]
    save = rebuild(_free(save, lane), rules)
    return save, _lines(c.lines[0] if c.cap is None and c.lines else None)


def interrupt(save: Save, rules: Rules, lane: LaneId) -> Save:
    """A ready tap whose card stops mid-completion (paused by a dry store, a requires turning false, or its speed
    falling to 0) ends at once: the lane is freed, the card keeps its work and any Pause, nothing lands and no line is
    emitted. The dry rule then runs again over what runs. Orders and the queue evaluate after it, as after a landing.
    A card whose work has reached its boundary is never interrupted: it has landed (DESIGN.txt, "Inputs against a
    dry store")."""
    return rebuild(_free(save, lane), rules)


def complete(save: Save, rules: Rules, card: CardId) -> tuple[Save, tuple[LineKey, ...]]:
    """The COMPLETION handler, for a capped card whose work reached a completion, tapped or mixed: emit the
    completion's line, apply the outcome's non-store parts (its stores ran as rates) and, at the cap, `finished`. At
    the cap the card is completed: its work stops, every mix holding it greys, and a tap of it ends at this instant.
    Returns the lines in emission order."""
    c = index(rules).cards[card]
    n = counts.completions(save, rules, card)
    own = _lines(c.lines[min(n, len(c.lines)) - 1] if c.lines and n >= 1 else None)
    reaches_cap = n == counts.effective_cap(save, rules, card)
    save, lines = _apply(save, rules, c.outcome, False)
    if reaches_cap:
        save, fin = _apply(save, rules, c.finished, True)
        lines += fin
    return save, own + lines


def apply_outcome(save: Save, rules: Rules, outcome: Outcome) -> tuple[Save, tuple[LineKey, ...]]:
    """An outcome in field order (cards.Outcome); the lines it emits are its own."""
    return _apply(save, rules, outcome, True)


def completions(save: Save, rules: Rules, card: CardId) -> int:
    """The card's work // (work_s * BP) at save.time, however it was run (CardCount reads this)."""
    return counts.completions(save, rules, card)


def effective_cap(save: Save, rules: Rules, card: CardId) -> int | None:
    """CardDef.cap plus CardState.raised; None for a card without a cap."""
    return counts.effective_cap(save, rules, card)


def is_completed(save: Save, rules: Rules, card: CardId) -> bool:
    """The card has a cap and its completions have reached it: in the Completed set (DESIGN.txt, "Caps")."""
    return counts.is_completed(save, rules, card)


def greyed(save: Save, rules: Rules, mix: MixId) -> bool:
    """The saved mix, flattened, holds a completed card (DESIGN.txt, "Greyed mix")."""
    return counts.greyed(save, rules, mix)


def starved(save: Save, rules: Rules, store: StoreId) -> bool:
    """The store has run dry while something waits on it: a runner that is not a spent card is paused on it, or a tap a
    true order or the queue head names is blocked by an AtLeast on its value (DESIGN.txt, "Starved line", "SPENT")."""
    if store_value(save, store) != 0:
        return False
    paused = [p.runner for p in save.pauses if p.store == store]
    if paused and any(running(save, rules).runs.get(r, FULL).kind is not RunKind.SPENT for r in paused):
        return True
    for card in candidates(save, rules):
        b = blocker(save, rules, card) if tappable(save, rules, card) else None
        if b is not None and isinstance(b.condition, AtLeast) and b.condition.subject == StoreValue(store):
            return True
    return False


def is_unlocked(save: Save, rules: Rules, u: Unlock) -> bool:
    """True when rules.opening is None, else whether `u` is in save.unlocked."""
    return gates.is_unlocked(save, rules, u)


def chip_modifiers(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    """The effects of every chip shown now (unlocked and latched), in rules.chips order. Each stack is
    save.modifiers then these."""
    return gates.chip_modifiers(save, rules)


def discrete_value(save: Save, rules: Rules, subject: DiscreteSubject) -> int:
    """A discrete subject's value now: 0/1 for Unlocked and Running."""
    return discrete.discrete_value(save, rules, subject)


def _refusal(save: Save, rules: Rules, card: CardId) -> str | None:
    c = index(rules).cards.get(card)
    if c is None:
        return f"unknown card {card}"
    if not gates.is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id)):
        return f"card {card} is locked"
    if counts.is_completed(save, rules, card):
        return f"card {card} is completed"
    if lane_state(save, c.lane).card is not None:
        return f"lane {c.lane} is busy"
    return None


def _free(save: Save, lane: LaneId) -> Save:
    return replace(save, lanes=tuple(LaneState(ls.lane) if ls.lane == lane else ls for ls in save.lanes))


def written_by(c: CardDef) -> frozenset[LineKey]:
    """The line keys the card's own content holds: its completion lines, its outcome's and finished's lines and its
    failed tap's line. A chip's on_line that the card's outcome happens to show is the chip's, not the card's."""
    keys = (*c.lines, *c.outcome.lines, *c.finished.lines, *_lines(c.failed_line))
    return frozenset(keys)


def _lines(key: LineKey | None) -> tuple[LineKey, ...]:
    return () if key is None else (key,)


def _apply(save: Save, rules: Rules, o: Outcome, with_stores: bool) -> tuple[Save, tuple[LineKey, ...]]:
    """The outcome in field order (retire_orders, leaves, orders, joins, queues); with_stores False leaves its stores out (a card's ran as rates)."""
    if with_stores:
        save = replace(save, stores=tuple(_paid(save, rules, st, o) for st in save.stores))
    save = _raise(_unlock(replace(save, modifiers=save.modifiers + o.modifiers), rules, o.unlocks), o.raises)
    save = left(without_taps(save, o.retire_orders), rules, o.leaves)
    save = joined(installed(save, present_installs(save, rules, o.orders)), rules, o.joins)
    save = rebuild(_end_retired_taps(queued(save, rules, o.queues), rules), rules)
    for card in o.starts:
        save = tap(save, rules, TapCard(card), False)
    save, lines = first_shown(save, rules)
    return save, o.lines + lines


def _paid(save: Save, rules: Rules, st: StoreState, o: Outcome) -> StoreState:
    """The store with the outcome's quantity added, held to its cap; the very object when its value does not move."""
    v = st.segment.start_value
    paid = min(store_cap(save, rules, st.store), v + sum(a.quantity for a in o.stores if a.store == st.store))
    return st if paid == v else replace(st, segment=replace(st.segment, start_value=paid))


def first_shown(save: Save, rules: Rules) -> tuple[Save, tuple[LineKey, ...]]:
    """The save with every chip shown now marked seen, and the on_line of each shown for the first time in the save
    (DESIGN.txt, "Chips")."""
    now = shown_chips(save, rules)
    first = {c.id for c, seen in zip(rules.chips, save.chips_seen) if c.id in now and not seen}
    if not first:
        return save, ()
    seen = tuple(was or c.id in first for c, was in zip(rules.chips, save.chips_seen))
    return replace(save, chips_seen=seen), tuple(c.on_line for c in rules.chips if c.id in first and c.on_line is not None)


def _end_retired_taps(save: Save, rules: Rules) -> Save:
    """A tap of a card just retired ends at once, keeping its work, as an interrupt does (DESIGN.txt, "Retired")."""
    for ls in save.lanes:
        if ls.card is not None and counts.is_retired(save, rules, ls.card):
            save = _free(save, ls.lane)
    return save


def _unlock(save: Save, rules: Rules, unlocks: tuple[Unlock, ...]) -> Save:
    if rules.opening is None:
        return save
    return replace(save, unlocked=tuple(sorted(set(save.unlocked) | set(unlocks), key=unlock_key)))


def _raise(save: Save, raises: tuple[CapRaise, ...]) -> Save:
    """Add each raise to its card's CardState (a still card gets one); rebuild puts the tuple in rules order."""
    for r in raises:
        have = counts.card_state(save, r.card)
        kept = tuple(cs for cs in save.cards if cs.card != r.card)
        now = CardState(r.card, Segment(save.time, 0, 0), r.by) if have is None else replace(have, raised=have.raised + r.by)
        save = replace(save, cards=kept + (now,))
    return save
