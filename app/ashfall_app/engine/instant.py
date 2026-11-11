"""Resolving one instant: handle events in (kind, sequence) order until none is pending, evaluating orders and the
queue whenever a latch changed or the queue popped, and clearing pauses whenever the running mix changed (DESIGN.txt,
"Order mix"). Once the instant's firings reach the cap, evaluation is suspended for the rest of it and a CascadeLimit
is recorded; events still resolve. Once nothing is pending and evaluation has ended, the settle decides which lanes
repeat their tap (retap.py, DESIGN.txt "REPEATING TAPS"), which may land one and start the loop again."""
from dataclasses import replace

from . import retap
from .end import with_end
from .decisions import apply_order_verb, controlling_verb, with_running_mix
from .events import CascadeLimit, Event, EventKind
from .handlers import Emit, handle, ignore, landing_cards
from .ids import CardId, LaneId, LineKey
from .mixes import SwitchMix
from .rules import Rules
from .schedule import pending
from .state import Save

_SETTLE_GUARD = 1_000_000
"""Not the firing cap: a bound on handler work that only an engine bug could reach (handlers resolve what they
handle, and nothing but evaluation can re-create a condition). Hitting it is a bug, so it raises."""

_REPEAT_FROM = 8
"""Firings into an instant before _Repeats starts remembering its states: below it a chain costs less than hashing
a save at every firing would."""


class _Repeats:
    """Finds an instant's chain repeating before the cap (DESIGN.txt, "Firing cap"). The loop's state at the top of an
    iteration (the save, the work, the idle set, whether evaluation is owed, how many lines were emitted) and the
    firing count decide everything after it while the count is under the cap (held and suspended change only at the
    cap), so a state seen p firings ago runs the same p firings again until the cap: those whole periods can be
    counted without being run. The emitted count in the state means a period that emits a line is never skipped."""

    def __init__(self, emit: Emit) -> None:
        self._seen: dict[object, int] = {}
        self._emitted = 0
        self._emit = emit

    def emit(self, time: int, key: LineKey, card: CardId | None) -> None:
        self._emitted += 1
        self._emit(time, key, card)

    def skipped(self, state: tuple[Save, dict[tuple[EventKind, int], Event], set[tuple[EventKind, int]], bool],
                firings: int, cap: int) -> int:
        """The firings to count without running them: whole periods of a repeat that ends before the cap, else 0."""
        if firings < _REPEAT_FROM or firings >= cap:
            return 0
        save, work, idle, must_evaluate = state
        first = self._seen.setdefault((save, frozenset(work.items()), frozenset(idle), must_evaluate, self._emitted),
                                      firings)
        if first == firings:
            return 0
        self._seen.clear()
        period = firings - first
        return (cap - firings) // period * period


def resolve_instant(save: Save, rules: Rules, arrivals: list[Event], must_evaluate: bool, emit: Emit = ignore) -> Save:
    work: dict[tuple[EventKind, int], Event] = {(e.kind, e.sequence): e for e in arrivals}
    firings = 0
    suspended = False
    idle: set[tuple[EventKind, int]] = set()
    """Dry-store events that found nothing to pause (every consumer has a completion or landing still to handle at this
    instant): not offered again until something changes."""
    held: set[tuple[EventKind, int]] = set()
    """Mix orders' latch changes past the firing cap: left for the next instant where something else fires."""
    repeats = _Repeats(emit)
    crossing = retap.crossing(save, rules) if arrivals else frozenset[LaneId]()
    """Repeating taps that reached a completion as time came to this instant: a task change here lands them now."""
    while True:
        firings += repeats.skipped((save, work, idle, must_evaluate), firings, rules.max_firings_per_instant)
        for e in pending(save, rules):
            if (e.kind, e.sequence) not in idle | held:
                work[(e.kind, e.sequence)] = e
        if work:
            key = min(work)
            event = work.pop(key)
            if firings >= rules.max_firings_per_instant and _moves_mix(save, event):
                held.add(key)
                suspended = True
                continue
            before = save
            save, changed = handle(save, rules, event, repeats.emit, landing_cards(save, rules, work.values()))
            save = save if save is before else with_running_mix(before, rules, save)
            if save is before:
                idle |= {key} if event.kind is EventKind.STORE_LIMIT else set()
            else:
                idle.clear()
            must_evaluate = must_evaluate or changed
            firings += 1
            if firings > _SETTLE_GUARD:
                raise RuntimeError(f"engine bug: instant t={save.time} did not settle")
        elif must_evaluate:
            if firings >= rules.max_firings_per_instant:
                must_evaluate, suspended = False, True
            else:
                save, fired, must_evaluate = _evaluate(save, rules, repeats.emit)
                firings += fired
        else:
            settled, landed = retap.settle(save, rules, crossing)
            if settled is save:
                break
            save, must_evaluate, firings = settled, landed, firings + int(landed)
    if suspended:
        save = replace(save, cascade_count=save.cascade_count + 1, last_cascade=CascadeLimit(save.time, firings))
    return with_end(save, rules)


def _evaluate(save: Save, rules: Rules, emit: Emit) -> tuple[Save, int, bool]:
    """One step of evaluation, below the firing cap: the controlling verb applied (one firing). Returns the save, the
    firings it spent, and whether evaluation goes on at this instant once what it raised is handled: it does while
    the verb applied changed the save, and ends when there is none or it changed nothing (TOWNSFOLK, INSTALLED RULES AND
    OFFERS, "Evaluation applies every verb"). Every verb that applies changes the save by a new object, and one that
    changes nothing returns the save it was given."""
    verb = controlling_verb(save, rules)
    if verb is None:
        return save, 0, False
    after, lines = apply_order_verb(save, rules, verb)
    for key in lines:
        emit(save.time, key, None)
    return after, 1, after is not save


def _moves_mix(save: Save, event: Event) -> bool:
    """A latch change of an order whose verb is a SwitchMix: it changes the running mix, and so rates, with no verb
    applied, which is why the firing cap holds it back (DESIGN.txt, "Firing cap")."""
    return event.kind is EventKind.LATCH and isinstance(save.orders[event.sequence].then, SwitchMix)
