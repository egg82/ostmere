"""The engine's entry points: pure functions over immutable saves and rules.

Every function takes rules that pass validate_rules. A time argument before save.time raises TimeOrderError.
Semantics live in DESIGN.txt: "Same instant", "Firing cap", "Cap", "Running dry".
"""
from collections.abc import Callable
from dataclasses import dataclass, replace

from .cards import LaneState
from .checks import check_modifiers
from .context import DecisionContext, decision_context
from .decisions import apply_verb, failed_tap, latch_now
from .errors import TimeOrderError
from .events import Event
from .handlers import Emit, ignore
from .ids import CardId, LineKey, SkillId, StoreId
from .index import index
from .instant import resolve_instant
from .motion import store_segment
from .mixes import SpentShare
from .modifiers import Explanation, Modifier, RateRef
from .rates import FULL, line, running, work_line
from .rebuild import rebuild, shift
from .rulelog import RuleChange, rule_changes
from .rules import Rules
from .schedule import events
from .segments import Segment
from .phases import level_shown
from .state import Save, SkillState, StoreState
from .unlocks import unlock_key
from .units import BP
from .verbs import Verb
from .work import first_shown


def new_save(rules: Rules, modifiers: tuple[Modifier, ...] = ()) -> Save:
    """A save at time 0: each store at its initial value, each skill at XP 0, no mixes, no orders, an empty queue,
    nothing active, the unlock set rules.opening. `modifiers` are the save's starting modifier stack. Time 0 is
    resolved like any instant (DESIGN.txt, "Instant 0"): triggers already true have fired, chips already true are
    latched, unlocked standing actions run in the segments. Its lines are not returned."""
    check_modifiers(modifiers)
    opening = () if rules.opening is None else tuple(sorted(set(rules.opening), key=unlock_key))
    save = Save(
        time=0,
        stores=tuple(StoreState(s.id, Segment(0, s.initial, 0)) for s in rules.stores),
        skills=tuple(SkillState(s.id, Segment(0, 0, 0)) for s in rules.skills),
        mixes=(), active=None, pauses=(), orders=(), latches=(), queue=(), modifiers=modifiers,
        lanes=tuple(LaneState(lane) for lane in index(rules).lanes), unlocked=opening,
        chips=(False,) * len(rules.chips), chips_seen=(False,) * len(rules.chips), fired=(False,) * len(rules.triggers),
    )
    save, _ = first_shown(replace(save, chips=tuple(latch_now(save, rules, c.when) for c in rules.chips)), rules)
    return resolve_instant(rebuild(save, rules), rules, [], False)


def advance(save: Save, rules: Rules, t: int) -> Save:
    """The save at time t, resolving every event with time <= t in order.

    advance(advance(s, r, t1), r, t2) == advance(s, r, t2) for s.time <= t1 <= t2, and advance(s, r, s.time) == s.
    """
    return _advance(save, rules, t, ignore)[0]


def _advance(save: Save, rules: Rules, t: int, emit: Emit, seen: list[RuleChange] | None = None,
             stop: Callable[[], bool] | None = None) -> tuple[Save, bool]:
    """The save, and whether it stopped short: `stop` returned True after an instant while instants at or before t
    remained, so the save is at that instant's time, not shifted to t. `seen`, when given, collects each instant's
    rule changes."""
    if t < save.time:
        raise TimeOrderError(f"t={t} is before the save's time {save.time}")
    stopping = False
    while True:
        upcoming = [e for e in events(save, rules) if e.time > save.time]
        if not upcoming:
            break
        at = min(e.time for e in upcoming)
        if at > t:
            break
        if stopping:
            return save, True
        arrivals = [e for e in upcoming if e.time == at]
        resolved = resolve_instant(rebuild(shift(save, rules, at), rules), rules, arrivals, False, emit)
        if seen is not None:
            seen.extend(rule_changes(save, resolved, rules))
        save = resolved
        stopping = stop is not None and stop()
    return (save if t == save.time else shift(save, rules, t)), False


def decide(save: Save, rules: Rules, t: int, verb: Verb) -> Save:
    """Advance to t, apply the player's verb, then resolve the instant (verbs may trigger evaluation, see verbs.py).

    decide(s, r, t, v) == decide(advance(s, r, t), r, t, v). An invalid verb raises InvalidVerbError.
    """
    return _decide(save, rules, t, verb, ignore)[1]


def _decide(save: Save, rules: Rules, t: int, verb: Verb, emit: Emit,
            seen: list[RuleChange] | None = None) -> tuple[Save, Save, CardId | None]:
    """The save advanced to t before the verb, the save after it, and the card of a failed tap (its failed_line emitted
    at t). `seen`, when given, collects the rule changes of the advance and of the decision's instant."""
    before, _ = _advance(save, rules, t, emit, seen)
    save, must_evaluate, lines = apply_verb(before, rules, verb)
    for key in lines:
        emit(t, key, None)
    failed = failed_tap(before, rules, verb)
    line = None if failed is None else index(rules).cards[failed].failed_line
    if failed is not None and line is not None:
        emit(t, line, failed)
    after = resolve_instant(save, rules, [], must_evaluate, emit)
    if seen is not None:
        seen.extend(rule_changes(before, after, rules))
    return before, after, failed


def next_event(save: Save, rules: Rules) -> Event | None:
    """The first event strictly after save.time, or None if none will ever happen ("runs indefinitely").

    Between save.time and that event's time every segment is exact: value(s, r, x, t) == value_at(segment(s, r, x), t).
    """
    upcoming = [e for e in events(save, rules) if e.time > save.time]
    return min(upcoming) if upcoming else None


def value(save: Save, rules: Rules, store: StoreId, t: int) -> int:
    """A store's quantity at t >= save.time; equal to reading advance(save, rules, t). Never changes the save."""
    return segment(advance(save, rules, t), rules, store).start_value


def segment(save: Save, rules: Rules, store: StoreId) -> Segment:
    """A store's current segment (start == save.time): what the client samples until next_event."""
    return store_segment(save, rules, store)


def xp(save: Save, rules: Rules, skill: SkillId, t: int) -> int:
    """A skill's XP at t >= save.time, as value() is for stores."""
    return next(st.xp.start_value for st in advance(save, rules, t).skills if st.skill == skill)


def level(save: Save, rules: Rules, skill: SkillId, t: int) -> int:
    """The skill's shown level at t: phases.level_shown of its phase and XP then; with rules.prestige None,
    level_for(rules.curve, xp(save, rules, skill, t))."""
    st = next(st for st in advance(save, rules, t).skills if st.skill == skill)
    return level_shown(rules.curve, rules.prestige, st.phase.phase, st.xp.start_value)


def explain(save: Save, rules: Rules, ref: RateRef) -> Explanation:
    """Why `ref` is this number now: base from rules (base_den > 1 for a card's lump line), the effective share
    (a card's flattened mix share, BP for an unlocked standing action or a card tapped ready, else 0), every modifier
    entry that
    applies with its source (LaneSpeed entries retargeted at ref), and its Run. Equal to modifiers.modified_rate on
    those inputs (DESIGN.txt, "Explain").

    A store's segment rate is the sum of its MAKE explanations minus its COST explanations, except at a limit (cap
    or empty) where it is clamped to 0. A mix card receiving a paused or spent card's share lists each in
    `gained`, its share the saved one plus theirs (DESIGN.txt, "SPENT").
    """
    now = running(save, rules)
    return _sourced(line(save, rules, ref, now.shares.get(ref.runner, 0), now.runs.get(ref.runner, FULL)),
                    now.gained.get(ref.runner, ()))


def _sourced(e: Explanation, gained: tuple[SpentShare, ...]) -> Explanation:
    """A kept line names no source of its share; the reader's gets the cards it receives from."""
    return replace(e, gained=gained) if gained else e


@dataclass(frozen=True)
class Line:
    """One log line: a content key emitted at engine time `time`. `seq` numbers the lines of one instant within one
    Step, from 0, in emission order: (time, seq) is unique within a Step, not across Steps. `card`: the card whose
    completion, tap or failed tap wrote it (one of work.written_by's keys), however the card was run; None for a
    chip's line and a trigger's. Lines are never stored on the save (DESIGN.txt, "Lines")."""

    time: int
    seq: int
    key: LineKey
    card: CardId | None = None


@dataclass(frozen=True)
class Step:
    """A save and the lines emitted on the way to it, in (time, seq) order. failed: the card of the player's TapCard
    when the decision was a failed tap (decide_logged only)."""

    save: Save
    lines: tuple[Line, ...]
    failed: CardId | None = None
    context: DecisionContext | None = None
    """What held as the decision was made, before it applied (decide_logged only; context.py)."""
    rule_changes: tuple[RuleChange, ...] = ()
    """Each rule start and let-go on the way, in time order (rulelog.py)."""
    stopped_short: bool = False
    """advance_logged with a stop only: the stop ended it with instants at or before t still to resolve, so save.time
    is the last resolved instant's, < t (DESIGN.txt, "Bounded advance")."""


def advance_logged(save: Save, rules: Rules, t: int, stop: Callable[[], bool] | None = None) -> Step:
    """advance(save, rules, t), plus the lines emitted at instants in (save.time, t].

    Its save == advance(save, rules, t). Split: the lines of s -> t1 followed by those of t1 -> t2 equal the lines
    of s -> t2 (seq restarts at each instant, so a split never renumbers).

    `stop`, when given, is asked after each instant resolves; True while instants at or before t remain ends the
    call there, stopped_short. Asking again from that save with the same t continues it: the chunks' saves, lines
    and rule_changes, concatenated, equal one call without a stop.
    """
    lines, emit = recorder()
    seen: list[RuleChange] = []
    done, short = _advance(save, rules, t, emit, seen, stop)
    return Step(done, numbered(lines), rule_changes=tuple(seen), stopped_short=short)


def decide_logged(save: Save, rules: Rules, t: int, verb: Verb) -> Step:
    """decide(save, rules, t, verb), plus the lines of the advance to t and of the decision's instant; the decision's
    lines continue the seq of the advance's lines at t. A failed tap's Step names its card."""
    lines, emit = recorder()
    seen: list[RuleChange] = []
    before, after, failed = _decide(save, rules, t, verb, emit, seen)
    return Step(after, numbered(lines), failed, decision_context(before, rules, verb), tuple(seen))


def explain_work(save: Save, rules: Rules, card: CardId) -> Explanation:
    """Why a card's bar fills at this speed: base BP per second, its share (BP for a tap, its mix share otherwise), the
    WorkRef and LaneSpeed entries aimed at it (with chip effects, sources named, each retargeted at the WorkRef), and
    its Run. ref is WorkRef(card); per_hour is work units per second, the formula rounded down (DESIGN.txt, "Work",
    "Explain"). A tapped card explains its tap; else a card the running mix holds explains its mix share and Run (per_hour
    0 while paused, waiting, greyed or yielded); else, as a tap started now."""
    now = running(save, rules)
    return _sourced(work_line(save, rules, card, now.shares.get(card, BP), now.runs.get(card, FULL)),
                    now.gained.get(card, ()))


def recorder() -> tuple[list[tuple[int, LineKey, CardId | None]], Emit]:
    found: list[tuple[int, LineKey, CardId | None]] = []

    def emit(time: int, key: LineKey, card: CardId | None) -> None:
        found.append((time, key, card))

    return found, emit


def numbered(found: list[tuple[int, LineKey, CardId | None]]) -> tuple[Line, ...]:
    """Emission order is time order; seq counts the lines already emitted at the same instant."""
    return tuple(Line(time, sum(1 for t, _, _ in found[:i] if t == time), key, card)
                 for i, (time, key, card) in enumerate(found))
