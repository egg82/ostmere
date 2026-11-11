"""Renames: every id in a save (or an outcome) through a table of Rename, each by the renames of its own kind.

Semantics: DESIGN.txt, "Renames". Applied transitively (a -> b, b -> c maps a to c); a cycle raises RebaseError. A
runner is renamed as a standing action or a card by what the manifest declares it to be; one it does not declare is
left as it is (an order may name a card no rules have).
"""
from collections.abc import Iterable
from dataclasses import dataclass, replace

from .cards import Amount, CapRaise, CardState, Join, LaneState, Leave, Outcome, RuleInstall
from .errors import RebaseError
from .answers import AnswerOffer
from .ids import ActionId, AnswerId, CardId, IdKind, LaneId, NodeId, OfferId, Runner, SkillId, SourceId, StoreId
from .lanes import TapCard
from .mixes import CardShare, Component, Mix
from .modifiers import LaneSpeed, Modifier, RateRef, SideStrength, StoreCap, Target, ThreatStrength, WorkRef
from .orders import (
    AfterTime, CardCount, Condition, LaneRules, Order, OrderVerb, QueueEntry, Running, SkillLevel, StoreValue, Subject,
    Unlocked,
)
from .state import ParkedRank, Pause, PhaseState, Save, SkillState, StoreState
from .unlocks import Unlock, UnlockKind


@dataclass(frozen=True)
class Rename:
    """`old` of `kind` is now `new` (content keeps every rename ever released: renames.toml)."""

    kind: IdKind
    old: str
    new: str


_UNLOCK_KINDS = {
    UnlockKind.ACTION: IdKind.STANDING, UnlockKind.CARD: IdKind.CARD, UnlockKind.RETIRED: IdKind.CARD,
    UnlockKind.SKILL: IdKind.SKILL, UnlockKind.STORE: IdKind.STORE, UnlockKind.CHIP: IdKind.CHIP,
    UnlockKind.FEATURE: IdKind.FEATURE, UnlockKind.OFFER: IdKind.OFFER, UnlockKind.ANSWERED: IdKind.OFFER,
    UnlockKind.ANSWER: IdKind.ANSWER, UnlockKind.JOINED: IdKind.LANE, UnlockKind.ENTRY: IdKind.ENTRY,
    UnlockKind.NOTE: IdKind.NOTE, UnlockKind.LEFT: IdKind.LANE,
}


class Renamer:
    """The renames as a lookup; `standing` and `cards` are the runner ids the save's manifest declares."""

    def __init__(self, renames: Iterable[Rename], standing: Iterable[str] = (), cards: Iterable[str] = ()) -> None:
        self._table: dict[IdKind, dict[str, str]] = {k: {} for k in IdKind}
        for r in renames:
            self._table[r.kind][r.old] = r.new
        self._standing = frozenset(standing)
        self._cards = frozenset(cards)

    def id(self, kind: IdKind, x: str) -> str:
        """`x` through every rename of its kind, transitively."""
        table, seen = self._table[kind], {x}
        while x in table:
            x = table[x]
            if x in seen:
                raise RebaseError(kind, x)
            seen.add(x)
        return x

    def store(self, x: StoreId) -> StoreId:
        return StoreId(self.id(IdKind.STORE, x))

    def card(self, x: CardId) -> CardId:
        """A card the manifest declares, renamed; any other (an order may name a card no rules have) as it is."""
        return CardId(self.id(IdKind.CARD, x)) if x in self._cards else x

    def runner(self, x: Runner) -> Runner:
        if x in self._standing:
            return ActionId(self.id(IdKind.STANDING, x))
        return self.card(CardId(x)) if x in self._cards else x

    def unlock(self, u: Unlock) -> Unlock:
        return Unlock(u.kind, self.id(_UNLOCK_KINDS[u.kind], u.id))


def _phase(ps: PhaseState, m: Renamer) -> PhaseState:
    """A phase with each pick's and parked rank's node renamed (IdKind.NODE)."""
    if not ps.picks and not ps.parked:
        return ps
    return replace(ps, picks=tuple(NodeId(m.id(IdKind.NODE, n)) for n in ps.picks),
                   parked=tuple(ParkedRank(NodeId(m.id(IdKind.NODE, p.node)), p.due) for p in ps.parked))


def renamed_save(save: Save, m: Renamer) -> Save:
    """Every id in the save renamed; positions (chips, fired) are left to the caller, which reads them by manifest."""
    return replace(
        save,
        stores=tuple(StoreState(m.store(st.store), st.segment) for st in save.stores),
        skills=tuple(SkillState(SkillId(m.id(IdKind.SKILL, st.skill)), st.xp, _phase(st.phase, m)) for st in save.skills),
        mixes=tuple(_mix(x, m) for x in save.mixes),
        pauses=tuple(Pause(m.runner(p.runner), m.store(p.store), p.resume_at) for p in save.pauses),
        orders=tuple(Order(condition(o.when, m), _verb(o.then, m)) for o in save.orders),
        queue=tuple(QueueEntry(_verb(e.verb, m), condition(e.until, m)) for e in save.queue),
        modifiers=tuple(modifier(x, m) for x in save.modifiers),
        lanes=tuple(_lane(ls, m) for ls in save.lanes),
        cards=tuple(CardState(m.card(cs.card), cs.work, cs.raised) for cs in save.cards),
        unlocked=tuple(m.unlock(u) for u in save.unlocked),
    )


def renamed_outcome(o: Outcome, m: Renamer) -> Outcome:
    """An outcome with every id renamed (its line keys are text, not ids, and are left as they are)."""
    return replace(
        o, stores=tuple(Amount(m.store(a.store), a.quantity) for a in o.stores),
        unlocks=tuple(m.unlock(u) for u in o.unlocks), modifiers=tuple(modifier(x, m) for x in o.modifiers),
        raises=tuple(CapRaise(m.card(r.card), r.by) for r in o.raises), starts=tuple(m.card(c) for c in o.starts),
        orders=tuple(RuleInstall(m.card(i.card), i.first) for i in o.orders), queues=tuple(m.card(c) for c in o.queues),
        joins=tuple(Join(LaneId(m.id(IdKind.LANE, j.lane)), j.mix, None if j.card is None else m.card(j.card))
                    for j in o.joins),
        retire_orders=tuple(m.card(c) for c in o.retire_orders),
        leaves=tuple(Leave(LaneId(m.id(IdKind.LANE, x.lane)), tuple(ActionId(m.id(IdKind.STANDING, a)) for a in x.stops))
                     for x in o.leaves))


def condition(c: Condition, m: Renamer) -> Condition:
    return c if isinstance(c, AfterTime) else replace(c, subject=_subject(c.subject, m))


def modifier(x: Modifier, m: Renamer) -> Modifier:
    return Modifier(_target(x.target, m), x.kind, x.amount_bp, SourceId(m.id(IdKind.SOURCE, x.source)))


def _subject(s: Subject, m: Renamer) -> Subject:
    if isinstance(s, StoreValue):
        return StoreValue(m.store(s.store))
    if isinstance(s, SkillLevel):
        return SkillLevel(SkillId(m.id(IdKind.SKILL, s.skill)))
    if isinstance(s, CardCount):
        return CardCount(m.card(s.card))
    if isinstance(s, Running):
        return Running(m.runner(s.runner))
    if isinstance(s, LaneRules):
        return LaneRules(LaneId(m.id(IdKind.LANE, s.lane)))
    return Unlocked(m.unlock(s.unlock))


def _target(t: Target, m: Renamer) -> Target:
    if isinstance(t, RateRef):
        return RateRef(m.runner(t.runner), t.kind, None if t.store is None else m.store(t.store))
    if isinstance(t, WorkRef):
        return WorkRef(m.card(t.card))
    if isinstance(t, LaneSpeed):
        return LaneSpeed(LaneId(m.id(IdKind.LANE, t.lane)))
    if isinstance(t, (SideStrength, ThreatStrength)):
        return t
    return StoreCap(m.store(t.store))


def _verb(v: OrderVerb, m: Renamer) -> OrderVerb:
    if isinstance(v, AnswerOffer):
        return AnswerOffer(OfferId(m.id(IdKind.OFFER, v.offer)), AnswerId(m.id(IdKind.ANSWER, v.answer)))
    return TapCard(m.card(v.card)) if isinstance(v, TapCard) else v


def _mix(x: Mix, m: Renamer) -> Mix:
    def component(c: Component) -> Component:
        return CardShare(m.card(c.card), c.share_bp) if isinstance(c, CardShare) else c
    return Mix(x.id, tuple(component(c) for c in x.components), x.layer)


def _lane(ls: LaneState, m: Renamer) -> LaneState:
    return replace(ls, lane=LaneId(m.id(IdKind.LANE, ls.lane)), card=None if ls.card is None else m.card(ls.card),
                   speed=None if ls.speed is None else tuple(_kept(x, m) for x in ls.speed))


def _kept(x: Modifier, m: Renamer) -> Modifier:
    """A tap's kept speed entry: a chip's is sourced by the chip's id (validation), so a chip rename renames it."""
    chip = m.id(IdKind.CHIP, x.source)
    return replace(modifier(x, m), source=SourceId(chip)) if chip != x.source else modifier(x, m)
