"""When an order's condition turns true or false, solved exactly from the current segments.

A time equal to save.time means "now" (pending); None means never under the current rates.
"""
from collections.abc import Iterable

from .counts import completions, unit, work_segment
from .discrete import discrete_value
from .index import index
from .motion import store_segment
from .memo import SaveMemo
from .orders import (
    AfterTime, AtLeast, CardCount, Condition, LaneRules, Running, SkillLevel, StoreValue, Subject, Unlocked,
)
from .rules import Rules
from .segments import Segment, reach_time
from .phases import counted_xp, level_counted
from .state import Save, SkillState


def subject_value(save: Save, rules: Rules, subject: Subject) -> int:
    if isinstance(subject, StoreValue):   # the commonest first
        return _stored(save, subject.store)
    if isinstance(subject, CardCount):
        return _count(save, rules, subject)
    if isinstance(subject, SkillLevel):
        return _level(save, rules, subject)
    return discrete_value(save, rules, subject)


def subject_values(save: Save, rules: Rules, subjects: Iterable[Subject]) -> list[int]:
    """subject_value of each, the stores' values fetched as one dict."""
    stored = _stored_values(save)
    return [stored[s.store] if isinstance(s, StoreValue) else subject_value(save, rules, s) for s in subjects]


def is_true(save: Save, rules: Rules, cond: Condition) -> bool:
    """The condition read plainly (no latch): what makes a latch rise, and what pops a queue head."""
    if isinstance(cond, AfterTime):
        return save.time >= cond.time
    v = subject_value(save, rules, cond.subject)
    return v >= cond.value if isinstance(cond, AtLeast) else v <= cond.value


def all_true(save: Save, rules: Rules, conds: tuple[Condition, ...]) -> bool:
    return all(is_true(save, rules, c) for c in conds)


def can_fall(cond: Condition) -> bool:
    """Whether the condition, once true, can turn false: not an AfterTime, nor an AtLeast on a card count, a skill
    level or an unlock (counts, levels and unlocks only grow)."""
    if isinstance(cond, AfterTime):
        return False
    return not (isinstance(cond, AtLeast) and isinstance(cond.subject, (CardCount, SkillLevel, Unlocked)))


def change_time(save: Save, rules: Rules, cond: Condition, latch: bool) -> int | None:
    """When a latch in state `latch` next changes: rises (false) or releases (true)."""
    return _fall_time(save, rules, cond) if latch else rise_time(save, rules, cond)


def rise_time(save: Save, rules: Rules, cond: Condition) -> int | None:
    return save.time if is_true(save, rules, cond) else unmet_rise_time(save, rules, cond)


def unmet_rise_time(save: Save, rules: Rules, cond: Condition) -> int | None:
    """rise_time of a condition that is not true now."""
    if isinstance(cond, AfterTime):
        return cond.time
    if isinstance(cond.subject, (Unlocked, Running, LaneRules)):
        return None  # discrete: it changes only at an instant, where the pending check sees it
    if isinstance(cond.subject, CardCount):
        return _count_time(save, rules, cond.subject, cond.value) if isinstance(cond, AtLeast) else None
    if isinstance(cond.subject, StoreValue):
        return reach_time(counting_segment(save, rules, cond.subject)[0], cond.value)
    return _level_time(save, rules, cond.subject, cond.value) if isinstance(cond, AtLeast) else None


def counting_segment(save: Save, rules: Rules, subject: CardCount | StoreValue) -> tuple[Segment, int]:
    """The segment a CardCount or StoreValue subject moves along, and what one of its units is in that segment's own:
    reach_time of it to `value * scale` is when the subject reaches `value`."""
    if isinstance(subject, CardCount):
        return work_segment(save, subject.card), unit(index(rules).cards[subject.card])
    return store_segment(save, rules, subject.store), 1


def _fall_time(save: Save, rules: Rules, cond: Condition) -> int | None:
    if isinstance(cond, AfterTime):
        return None
    v = subject_value(save, rules, cond.subject)
    if isinstance(cond, AtLeast):
        if v < cond.release:
            return save.time
        if isinstance(cond.subject, StoreValue):
            return reach_time(store_segment(save, rules, cond.subject.store), cond.release - 1)
        return None
    if v > cond.release:
        return save.time
    if isinstance(cond.subject, StoreValue):
        return reach_time(store_segment(save, rules, cond.subject.store), cond.release + 1)
    if isinstance(cond.subject, CardCount):
        return _count_time(save, rules, cond.subject, cond.release + 1)
    if not isinstance(cond.subject, SkillLevel):
        return None  # discrete: seen by the pending check at the instant it changes
    return _level_time(save, rules, cond.subject, cond.release + 1)


def _count(save: Save, rules: Rules, subject: CardCount) -> int:
    """Completions now: work.completions (the card's work // its work per completion)."""
    return completions(save, rules, subject.card)


def _count_time(save: Save, rules: Rules, subject: CardCount, count: int) -> int | None:
    """When the card's work segment reaches count * work_s * BP; None when its work is not rising."""
    return reach_time(work_segment(save, subject.card), count * unit(index(rules).cards[subject.card]))


def _level_time(save: Save, rules: Rules, subject: SkillLevel, level: int) -> int | None:
    """When the skill's level, counted across phases (phases.level_counted), reaches `level`; None past the curve's
    last level, or past its phase's top, which only the player's click lifts."""
    if level <= 1:
        return save.time
    st = _skill(save, subject)
    x = counted_xp(rules.curve, rules.prestige, st.phase.phase, level)
    return None if x is None else reach_time(st.xp, x)


_VALUES: SaveMemo[dict[str, int]] = SaveMemo()


def _stored(save: Save, store: str) -> int:
    """A store's value now, read off the save: running reads requires through here, and store_segment reads running."""
    return _stored_values(save)[store]


def _stored_values(save: Save) -> dict[str, int]:
    def build() -> dict[str, int]:
        found: dict[str, int] = {}
        for st in save.stores:
            found.setdefault(st.store, st.segment.start_value)
        return found
    return _VALUES.get(save, None, build)


_SKILLS: SaveMemo[dict[str, SkillState]] = SaveMemo()


def _skill(save: Save, subject: SkillLevel) -> SkillState:
    """Each skill's state by id, the first of an id as a scan finds it: one pass per save."""
    def build() -> dict[str, SkillState]:
        skills: dict[str, SkillState] = {}
        for k in save.skills:
            skills.setdefault(k.skill, k)
        return skills
    return _SKILLS.get(save, None, build)[subject.skill]


def _level(save: Save, rules: Rules, subject: SkillLevel) -> int:
    st = _skill(save, subject)
    return level_counted(rules.curve, rules.prestige, st.phase.phase, st.xp.start_value)
