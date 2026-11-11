"""The scheduler's triggers: the events of the unfired ones, and which are due at save.time (schedule.py)."""
from collections.abc import Sequence
from dataclasses import dataclass

from .conditions import all_true, counting_segment, is_true, subject_value, subject_values, unmet_rise_time
from .events import Event, EventKind
from .ids import SkillId
from .memo import PartsMemo
from .orders import AfterTime, AtLeast, CardCount, Condition, SkillLevel, StoreValue, Subject, Unlocked
from .rules import Rules
from .segments import Segment, reach_time
from .phases import counted_xp, level_counted
from .state import Save, SkillState


def _level_rise(save: Save, rules: Rules, level_xp: tuple[int, SkillState], value: int) -> int | None:
    """rise_time of AtLeast(SkillLevel, value), from the skill's counted level and state read once
    (conditions.rise_time, _level_time): now if reached, never past the curve's top or its phase's, else when the XP
    reaches the level's threshold."""
    level, st = level_xp
    if level >= value or value <= 1:
        return save.time
    x = counted_xp(rules.curve, rules.prestige, st.phase.phase, value)
    return None if x is None else reach_time(st.xp, x)



def triggers_now(save: Save, rules: Rules) -> list[Event]:
    """trigger_events at save.time: a trigger on an AtLeast is due once its subject has reached it, each subject read
    once for all the triggers on it, which are many."""
    unfired = _UNFIRED.get((rules, save.fired, save.unlocked), lambda: _unfired(save, rules))
    due: list[int] = []
    for k in save.skills:
        level = max(_counted(rules, k), 1)
        due += _reached(unfired.by_level.get(k.skill, ()), level)
    for found, value in zip(unfired.by_subject.values(), subject_values(save, rules, unfired.by_subject)):
        due += _reached(found, value)
    due += [i for i in unfired.rest if is_true(save, rules, rules.triggers[i].when)]
    due = [i for i in due if all_true(save, rules, rules.triggers[i].requires)]
    return [Event(save.time, EventKind.TRIGGER, i, rules.triggers[i].id) for i in sorted(due)]


def _reached(found: Sequence[tuple[int, int]], value: int) -> list[int]:
    """The indices of the (threshold, index) pairs, in threshold order, whose threshold `value` has reached."""
    out: list[int] = []
    for threshold, i in found:
        if threshold > value:
            break
        out.append(i)
    return out


@dataclass(frozen=True)
class _Unfired:
    by_level: dict[SkillId, list[tuple[int, int]]]
    """The triggers on a skill's level, as (level, index) in level order."""
    by_subject: dict[Subject, list[tuple[int, int]]]
    """The other AtLeast triggers, as (value, index) in value order by subject."""
    rest: tuple[int, ...]
    """The triggers on an AtMost or an AfterTime."""


_UNFIRED: PartsMemo[_Unfired] = PartsMemo()
"""Kept while save.fired and save.unlocked are the same tuples: a trigger fires, and something unlocks, a few times a
day."""


def _unfired(save: Save, rules: Rules) -> _Unfired:
    """The unfired triggers whose requires on unlocks hold, grouped by what they read. A require on an unlock reads
    save.unlocked alone, so one that fails leaves its trigger neither due nor scheduled until the unlocks change, and
    the memo is rebuilt then: a chain of offers each waiting on the last one's answer costs nothing per instant."""
    by_level: dict[SkillId, list[tuple[int, int]]] = {}
    by_subject: dict[Subject, list[tuple[int, int]]] = {}
    rest: list[int] = []
    for i, (trigger, fired) in enumerate(zip(rules.triggers, save.fired)):
        w = trigger.when
        if fired or not all(is_true(save, rules, c) for c in trigger.requires if _on_unlock(c)):
            continue
        if not isinstance(w, AtLeast):
            rest.append(i)
        elif isinstance(w.subject, SkillLevel):
            by_level.setdefault(w.subject.skill, []).append((w.value, i))
        else:
            by_subject.setdefault(w.subject, []).append((w.value, i))
    return _Unfired({s: sorted(f) for s, f in by_level.items()}, {s: sorted(f) for s, f in by_subject.items()},
                    tuple(rest))


def _on_unlock(c: Condition) -> bool:
    return not isinstance(c, AfterTime) and isinstance(c.subject, Unlocked)


def _level_times(save: Save, rules: Rules, level_xp: tuple[int, SkillState], pairs: Sequence[tuple[int, int]]
                 ) -> list[tuple[int, int | None]]:
    """(index, rise time) of the triggers on one skill's levels, its counted level and state read once. XP standing
    still never reaches a level it is not at."""
    resting = type(level_xp[1].xp) is Segment and level_xp[1].xp.rate == 0
    return [(i, save.time if level_xp[0] >= value or value <= 1 else None if resting else _level_rise(
        save, rules, level_xp, value)) for value, i in pairs]


def _subject_times(save: Save, rules: Rules, subject: Subject, pairs: Sequence[tuple[int, int]]
                   ) -> list[tuple[int, int | None]]:
    """(index, rise time) of the AtLeast triggers on one subject (not a skill's level), read once. A plain segment
    standing still (a store or a count at rest) never reaches a value it is not at; a discrete subject changes only at
    an instant."""
    v = subject_value(save, rules, subject)
    if not isinstance(subject, (CardCount, StoreValue)) or pairs[-1][0] <= v:
        return [(i, save.time if v >= value else None) for value, i in pairs]
    seg, scale = counting_segment(save, rules, subject)
    resting = type(seg) is Segment and seg.rate == 0
    return [(i, save.time if v >= value else None if resting else reach_time(seg, value * scale)) for value, i in pairs]


def trigger_events(save: Save, rules: Rules) -> list[Event]:
    """Each unfired trigger whose requires hold, at its condition's rise time, in trigger order (a skill's level and
    each other subject read once for all the triggers on it, which are many: tests/dayone/test_dayone_forecast.py holds
    the levels equal to rise_time)."""
    unfired = _UNFIRED.get((rules, save.fired, save.unlocked), lambda: _unfired(save, rules))
    times: list[tuple[int, int | None]] = []
    levels = {k.skill: (_counted(rules, k), k) for k in save.skills}
    for skill, pairs in unfired.by_level.items():
        times += _level_times(save, rules, levels[skill], pairs)
    for subject, pairs in unfired.by_subject.items():
        times += _subject_times(save, rules, subject, pairs)
    for i in unfired.rest:
        w = rules.triggers[i].when
        times.append((i, save.time if is_true(save, rules, w) else unmet_rise_time(save, rules, w)))
    holds: dict[Condition, bool] = {}   # the requires conditions, which triggers share
    return [Event(t, EventKind.TRIGGER, i, rules.triggers[i].id) for i, t in sorted(times, key=lambda x: x[0])
            if t is not None and all(_holds(save, rules, c, holds) for c in rules.triggers[i].requires)]


def _holds(save: Save, rules: Rules, cond: Condition, kept: dict[Condition, bool]) -> bool:
    if cond not in kept:
        kept[cond] = is_true(save, rules, cond)
    return kept[cond]


def _counted(rules: Rules, k: SkillState) -> int:
    return level_counted(rules.curve, rules.prestige, k.phase.phase, k.xp.start_value)
