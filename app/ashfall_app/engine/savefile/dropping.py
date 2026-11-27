"""Dropping: every reference a save holds to an id its manifest declared and the new rules lack, taken out of it.

Semantics: engine/design/, "Rebase", steps 3 and 4. What goes with a gone id: an order or queue entry whose condition names one,
an action naming one (the order goes when none is left), a modifier aimed at one, a pause of or on one, a mix's share
of a gone card, a lane's tap of one, and its unlock. An id the manifest never declared is left as it is (an order may
name a card no rules have: "Orders").
"""
from collections.abc import Mapping
from dataclasses import dataclass, replace

from ..offers.answers import AnswerKind, AnswerOffer
from ..core.ids import IdKind
from ..orders.lanes import TapCard
from ..mixes.mixes import CardShare, Mix
from ..modifiers.modifiers import LaneSpeed, Modifier, RateRef, StoreCap, WorkRef
from ..orders.orders import AfterTime, CardCount, Condition, Order, OrderVerb, Running, SkillLevel, StoreValue, Unlocked, pruned
from ..core.rules import Rules
from ..core.state import Save
from ..unlocks.unlocks import Unlock, UnlockKind

_UNLOCK_KINDS = {
    UnlockKind.ACTION: IdKind.STANDING, UnlockKind.CARD: IdKind.CARD, UnlockKind.RETIRED: IdKind.CARD,
    UnlockKind.SKILL: IdKind.SKILL, UnlockKind.STORE: IdKind.STORE, UnlockKind.CHIP: IdKind.CHIP,
    UnlockKind.FEATURE: IdKind.FEATURE, UnlockKind.OFFER: IdKind.OFFER, UnlockKind.ANSWERED: IdKind.OFFER,
    UnlockKind.ANSWER: IdKind.ANSWER, UnlockKind.JOINED: IdKind.LANE, UnlockKind.LEFT: IdKind.LANE,
}
"""The kind of id each unlock kind names; ENTRY and NOTE name journal ids no manifest declares, so none is dropped."""


@dataclass(frozen=True)
class Gone:
    """The ids the save's manifest declares that the new rules lack, by kind (an answer the new rules put under another
    offer counts as gone: the save's answer was to the old one)."""

    ids: Mapping[IdKind, frozenset[str]]

    def has(self, kind: IdKind, x: str) -> bool:
        return x in self.ids[kind]

    def runner(self, x: str) -> bool:
        return self.has(IdKind.STANDING, x) or self.has(IdKind.CARD, x)

    def unlock(self, u: Unlock) -> bool:
        kind = _UNLOCK_KINDS.get(u.kind)
        return kind is not None and self.has(kind, u.id)

    def counts(self) -> tuple[tuple[IdKind, int], ...]:
        """How many ids of each kind are gone, in IdKind order, kinds with none left out."""
        return tuple((k, len(self.ids[k])) for k in IdKind if self.ids[k])


def dropped_save(save: Save, gone: Gone, rules: Rules) -> Save:
    """The save without what names a gone id; stores, skills, chips, triggers and cards are left to the reshape, which
    builds them from the new rules. An AnswerKind order whose kind and role no offer of the new rules has goes too."""
    kept = [(k, latch) for o, latch in zip(save.orders, save.latches) if (k := _order(o, gone, rules)) is not None]
    return replace(
        save,
        orders=tuple(o for o, _ in kept), latches=tuple(latch for _, latch in kept),
        queue=tuple(e for e in save.queue if not _verb(e.verb, gone, rules) and not _condition(e.until, gone)),
        mixes=tuple(_mix(x, gone) for x in save.mixes),
        pauses=tuple(p for p in save.pauses if not gone.runner(p.runner) and not gone.has(IdKind.STORE, p.store)),
        modifiers=tuple(x for x in save.modifiers if not _modifier(x, gone)),
        lanes=tuple(replace(ls, card=None, speed=None) if ls.card is not None and gone.has(IdKind.CARD, ls.card)
                    else replace(ls, speed=tuple(x for x in ls.speed if not _modifier(x, gone)))
                    if ls.speed is not None else ls for ls in save.lanes),
        unlocked=tuple(u for u in save.unlocked if not gone.unlock(u)))


def _order(o: Order, gone: Gone, rules: Rules) -> Order | None:
    if _condition(o.when, gone) or any(_condition(g, gone) for g in o.unless):
        return None
    return pruned(o, lambda a: _verb(a, gone, rules))


def _condition(c: Condition, gone: Gone) -> bool:
    if isinstance(c, AfterTime):
        return False
    s = c.subject
    if isinstance(s, StoreValue):
        return gone.has(IdKind.STORE, s.store)
    if isinstance(s, SkillLevel):
        return gone.has(IdKind.SKILL, s.skill)
    if isinstance(s, CardCount):
        return gone.has(IdKind.CARD, s.card)
    if isinstance(s, Running):
        return gone.runner(s.runner)
    if isinstance(s, Unlocked):
        return gone.unlock(s.unlock)
    return gone.has(IdKind.LANE, s.lane)


def _verb(v: OrderVerb, gone: Gone, rules: Rules) -> bool:
    if isinstance(v, TapCard):
        return gone.has(IdKind.CARD, v.card)
    if isinstance(v, AnswerOffer):
        return gone.has(IdKind.OFFER, v.offer) or gone.has(IdKind.ANSWER, v.answer)
    if isinstance(v, AnswerKind):
        return not any(o.kind == v.kind and any(a.role == v.role for a in o.answers) for o in rules.offers)
    return False


def _modifier(x: Modifier, gone: Gone) -> bool:
    t = x.target
    if isinstance(t, RateRef):
        return gone.runner(t.runner) or (t.store is not None and gone.has(IdKind.STORE, t.store))
    if isinstance(t, WorkRef):
        return gone.has(IdKind.CARD, t.card)
    if isinstance(t, LaneSpeed):
        return gone.has(IdKind.LANE, t.lane)
    if isinstance(t, StoreCap):
        return gone.has(IdKind.STORE, t.store)
    return False


def _mix(x: Mix, gone: Gone) -> Mix:
    kept = tuple(c for c in x.components if not (isinstance(c, CardShare) and gone.has(IdKind.CARD, c.card)))
    return x if kept == x.components else replace(x, components=kept)
