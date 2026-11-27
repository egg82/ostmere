"""Fixture rules for the groups contract tests (engine design/groups.txt, "GROUPS (pooled lanes)", invariants 179-183). Built
from the engine's public types and that part alone.

G is a pooled lane (the group); P1-P3 are people whose `group` is G; Q1 is a person with no group. Every card is
uncapped unless said and makes one item a second at a full share. G holds GA (makes x) and GB (makes y); each person
has an own card of the same kind (PA makes x, PB makes y) and a one-off `tap` card (OFF, capped at 1, 20 s) for a
tap that takes the person's lane."""
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, CardDef, CardId, CardShare, Flow, Join, LaneDef, LaneId, Mark, Mix, MixId,
    Order, Outcome, PacingCurve, Rules, Save, SaveMix, SetOrders, SkillDef, SkillId, StoreDef, StoreId, SwitchMix, TapCard,
    TriggerDef, TriggerId, CardView, Verb, LaneState, advance, decide, new_save, per_hour, segment, validate_rules, value_at, view,
)

G = LaneId("g")
PEOPLE = (LaneId("p1"), LaneId("p2"), LaneId("p3"))
P1, P2, P3 = PEOPLE
Q1 = LaneId("q1")
X, Y = StoreId("x"), StoreId("y")
GA, GB = CardId("ga"), CardId("gb")
TOWN = MixId("town:main")
ALWAYS = AfterTime(0)
BIG = 10**6 * Q
PER_SECOND = per_hour(3600)
WORK = 10
OFF_S = 20


def own(lane: LaneId, which: str) -> CardId:
    return CardId(f"{lane}{which}")


def off(lane: LaneId) -> CardId:
    return CardId(f"{lane}off")


def cards(people: Sequence[LaneId] = PEOPLE) -> tuple[CardDef, ...]:
    out = [CardDef(GA, WORK, lane=G, makes=(Flow(X, PER_SECOND),)), CardDef(GB, WORK, lane=G, makes=(Flow(Y, PER_SECOND),))]
    for p in (*people, Q1):
        out += [CardDef(own(p, "a"), WORK, lane=p, makes=(Flow(X, PER_SECOND),)),
                CardDef(own(p, "b"), WORK, lane=p, makes=(Flow(Y, PER_SECOND),)),
                CardDef(off(p), OFF_S, lane=p, cap=1)]
    return tuple(out)


def lanes() -> tuple[LaneDef, ...]:
    return (LaneDef(G, True, pooled=True), *(LaneDef(p, True, group=G) for p in PEOPLE), LaneDef(Q1, True))


def world(triggers: tuple[TriggerDef, ...] = (), check: bool = True, **changes: Any) -> Rules:
    """The fixture rules with `changes` replaced; validated unless `check` is False (a test of the refusal)."""
    r = Rules(stores=(StoreDef(X, BIG), StoreDef(Y, BIG)), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**15,)), lanes=lanes(), cards=cards(), triggers=triggers)
    r = replace(r, **changes)
    if check:
        validate_rules(r)
    return r


def join(lane: LaneId, card: CardId | None, own_split: bool, at: int = 0, tid: str | None = None) -> TriggerDef:
    return TriggerDef(TriggerId(tid or f"join-{lane}"), AfterTime(at), Outcome(joins=(Join(lane, TOWN, card, own_split),)))


def mark(lane: LaneId, own_split: bool, card: CardId | None = None, at: int = 0, tid: str | None = None) -> TriggerDef:
    return TriggerDef(TriggerId(tid or f"mark-{lane}-{at}-{own_split}"), AfterTime(at), Outcome(marks=(Mark(lane, own_split, card),)))


def crew_triggers(k: int, card: CardId = GA) -> tuple[TriggerDef, ...]:
    """The first k people join unmarked at 0, in order; the first's join names `card` on G."""
    return tuple(join(p, card, False) for p in PEOPLE[:k])


def save_mix(shares: Sequence[CardShare]) -> SaveMix:
    return SaveMix(Mix(TOWN, tuple(shares)))


def split_mix(*shares: tuple[CardId, int]) -> SaveMix:
    return save_mix([CardShare(c, bp) for c, bp in shares])


def start(r: Rules, *verbs: Verb) -> Save:
    s = new_save(r)
    for v in verbs:
        s = decide(s, r, 0, v)
    return s


def stored(s: Save, r: Rules, store: StoreId, t: int) -> int:
    return value_at(segment(advance(s, r, t), r, store), t)


def card_view(s: Save, r: Rules, c: CardId, t: int) -> CardView:
    s2 = advance(s, r, t)
    return next(cv for cv in view(s2, r).cards if cv.card == c)


def work(s: Save, r: Rules, c: CardId, t: int) -> int:
    return value_at(card_view(s, r, c, t).bar, t)


def tap_orders(*taps: tuple[int, LaneId]) -> SetOrders:
    """The town's always rule the joins installed, then a one-off tap of each lane's `off` card at its time."""
    return SetOrders((Order(ALWAYS, SwitchMix(TOWN)), *(Order(AfterTime(at), TapCard(off(lane))) for at, lane in taps)))


def tap_order(at: int, lane: LaneId) -> SetOrders:
    return tap_orders((at, lane))


def lane_state(s: Save, lane: LaneId) -> LaneState:
    return next(ls for ls in s.lanes if ls.lane == lane)
