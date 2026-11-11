"""Fixture rules for the town's mix contract tests (engine DESIGN.txt, "THE TOWN'S MIX", invariants 90-97). Built from the
engine's public types only. Three ruled lanes: la and lb are people (each joins by a trigger's Join), lc is cure-shaped
and never joins. Every card takes 10 s a completion at full speed (a capped one, ac, takes 50 s)."""
from collections.abc import Mapping
from dataclasses import fields, is_dataclass, replace
from typing import TypeGuard

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, Amount, CardDef, CardId, CardShare, Flow, Join, LaneDef, LaneId, Mix, MixId,
    Order, Outcome, PacingCurve, Rules, Save, SaveMix, SetOrders, SkillDef, SkillId, StoreDef, StoreId, SwitchMix,
    TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Verb, advance, decide, new_save, per_hour, segment, unlock_key,
    value_at, view,
)

LA, LB, LC = LaneId("la"), LaneId("lb"), LaneId("lc")
X, Y, W, V = StoreId("x"), StoreId("y"), StoreId("w"), StoreId("v")
K = SkillId("k")
A1, A2, AC, B1, B2, C1 = CardId("a1"), CardId("a2"), CardId("ac"), CardId("b1"), CardId("b2"), CardId("c1")
H1, H2 = CardId("h1"), CardId("h2")
TM, TM2 = MixId("town:main"), MixId("town:two")
HM1, HM2 = MixId("hands1"), MixId("hands2")
ALWAYS = AfterTime(0)
BIG = 10**6 * Q
PER_SECOND = per_hour(3600)
WORK = 10

CARDS = (
    CardDef(A1, WORK, lane=LA, makes=(Flow(X, PER_SECOND),), outcome=Outcome(stores=(Amount(Y, Q),))),
    CardDef(A2, WORK, lane=LA, makes=(Flow(W, PER_SECOND),)),
    CardDef(AC, 50, lane=LA, cap=1),
    CardDef(B1, WORK, lane=LB, makes=(Flow(V, PER_SECOND),)),
    CardDef(B2, WORK, lane=LB, makes=(Flow(W, PER_SECOND),)),
    CardDef(C1, WORK, lane=LC),
    CardDef(H1, WORK, skill=K, xp_per_hour=PER_SECOND),
    CardDef(H2, WORK),
)
"""a1: repeat-eligible (uncapped, no inputs), a continuous x line and a y lump per completion. ac: capped, a one-off."""

TOWN_RULE = Order(ALWAYS, SwitchMix(TM))


def world(triggers: tuple[TriggerDef, ...] = (), cards: tuple[CardDef, ...] = (),
          opening: tuple[Unlock, ...] | None = None) -> Rules:
    stores = tuple(StoreDef(s, BIG) for s in (X, Y, W, V))
    return Rules(stores=stores, skills=(SkillDef(K),), standing=(), curve=PacingCurve((10**15,)),
                 lanes=(LaneDef(LA, True), LaneDef(LB, True), LaneDef(LC, True)), cards=CARDS + cards,
                 triggers=triggers, opening=opening)


def joiner(tid: str, lane: LaneId, mix: MixId, card: CardId | None, at: int = 0) -> TriggerDef:
    """A trigger whose outcome is one Join (time 0 is resolved by new_save)."""
    return TriggerDef(TriggerId(tid), AfterTime(at), Outcome(joins=(Join(lane, mix, card),)))


def always(card: CardId) -> Order:
    return Order(ALWAYS, TapCard(card))


def start(r: Rules, *verbs: Verb, at: int = 0) -> Save:
    s = new_save(r)
    for v in verbs:
        s = decide(s, r, at, v)
    return s


def orders(*o: Order) -> SetOrders:
    return SetOrders(tuple(o))


def hands_mixes() -> tuple[Verb, ...]:
    return SaveMix(Mix(HM1, (CardShare(H1, BP),))), SaveMix(Mix(HM2, (CardShare(H2, BP),)))


def stored(s: Save, r: Rules, store: StoreId, t: int) -> int:
    return value_at(segment(advance(s, r, t), r, store), t)


def card_view(s: Save, r: Rules, c: CardId, t: int):
    s2 = advance(s, r, t)
    return next(cv for cv in view(s2, r).cards if cv.card == c), s2


def work_done(s: Save, r: Rules, c: CardId, t: int) -> int:
    cv, _ = card_view(s, r, c, t)
    return value_at(cv.bar, t)


def count(s: Save, r: Rules, c: CardId, t: int) -> int:
    return card_view(s, r, c, t)[0].completions


def lane_card(s: Save, lane: LaneId) -> CardId | None:
    return next(ls.card for ls in s.lanes if ls.lane == lane)


def joined(s: Save, lane: LaneId) -> bool:
    return Unlock(UnlockKind.JOINED, lane) in s.unlocked


def _is_tuple(v: object) -> TypeGuard[tuple[object, ...]]:
    return isinstance(v, tuple)


def _sub(v: object, ids: Mapping[str, str]) -> object:
    if isinstance(v, str):
        return ids.get(v, v)
    if _is_tuple(v):
        return tuple(_sub(x, ids) for x in v)
    if is_dataclass(v) and not isinstance(v, type):
        return replace(v, **{f.name: _sub(getattr(v, f.name), ids) for f in fields(v)})
    return v


def sub_rules(r: Rules, ids: Mapping[str, str]) -> Rules:
    out = _sub(r, ids)
    assert isinstance(out, Rules)
    return out


def sub_save(s: Save, ids: Mapping[str, str]) -> Save:
    """What a save says under renamed ids, the unlock set re-sorted."""
    out = _sub(s, ids)
    assert isinstance(out, Save)
    return replace(out, unlocked=tuple(sorted(out.unlocked, key=unlock_key)))
