"""What an entry's conditions and modifiers name, in authoring units, to the engine's (fixed point). Pure."""
from typing import TYPE_CHECKING

from ..engine import (
    HANDS, ActionId, AfterTime, AtLeast, AtMost, CardCount, CardId, ChainReach, Condition, FlowKind, LaneId, LaneRules, LaneSpeed,
    Modifier, ModifierKind, RateRef, Runner, Running, SideId, SideStrength, SkillId, SkillLevel, SourceId, StoreCap,
    StoreId, StoreValue, Subject, Target, ThreatId, ThreatStrength, Unlock, Unlocked, UnlockKind, WorkRef, units,
)

if TYPE_CHECKING:
    from .entries import ConditionEntry, ModifierEntry


def _runner(id_: str, cards: set[str]) -> Runner:
    """Standing actions and cards share one id namespace; the opening's card list says which this is."""
    return CardId(id_) if id_ in cards else ActionId(id_)


def modifier(m: "ModifierEntry", cards: set[str]) -> Modifier:
    target: Target
    if m.target == "rate":
        assert m.flow is not None
        target = RateRef(_runner(m.id, cards), FlowKind(m.flow), None if m.store is None else StoreId(m.store))
    elif m.target == "work":
        target = WorkRef(CardId(m.id))
    elif m.target == "cap":
        target = StoreCap(StoreId(m.id))
    elif m.target == "side":
        target = SideStrength(SideId(m.id))
    elif m.target == "threat":
        target = ThreatStrength(ThreatId(m.id))
    elif m.target == "chain":
        target = ChainReach(CardId(m.id))
    else:
        target = LaneSpeed(LaneId(HANDS if m.id == HANDS else m.id))
    return Modifier(target, ModifierKind(m.kind), m.amount_bp, SourceId(m.source))


def levels(c: "ConditionEntry") -> tuple[int, int]:
    """(value, release) as the engine reads them: on a store, whole items over `every` in quantity units; on a level,
    count or 0/1, as written. Release defaults to value. Every loader reader of a threshold reads it here; the loader
    has checked a store's divides exactly (refs.py)."""
    release = c.value if c.release is None else c.release
    if c.subject_kind != "store":
        return c.value, release
    return units(c.value) // c.every, units(release) // c.every


def condition(c: "ConditionEntry", cards: set[str]) -> Condition:
    if c.test == "after_time":
        return AfterTime(c.value)
    value, release = levels(c)
    subject = _subject(c, cards)
    return AtLeast(subject, value, release) if c.test == "at_least" else AtMost(subject, value, release)


def _subject(c: "ConditionEntry", cards: set[str]) -> Subject:
    assert c.id is not None
    if c.subject_kind == "store":
        return StoreValue(StoreId(c.id))
    if c.subject_kind == "skill_level":
        return SkillLevel(SkillId(c.id))
    if c.subject_kind == "card_count":
        return CardCount(CardId(c.id))
    if c.subject_kind == "running":
        return Running(_runner(c.id, cards))
    if c.subject_kind == "lane_rules":
        return LaneRules(LaneId(c.id))
    assert c.unlock_kind is not None
    return Unlocked(Unlock(UnlockKind(c.unlock_kind), c.id))
