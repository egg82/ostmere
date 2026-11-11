"""Evaluation applies every verb that can act (DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS"): two lanes
driven at one instant, a tap order beside the queue's head, a tap at speed 0 skipped, a chip turning that evaluates,
and a queued switch's mix at a pop past the cap. Each failed under one verb per evaluation."""
from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, ActionId, AfterTime, AtLeast, AtMost, CardCount, CardDef, CardId, CardShare,
    ChipDef, ChipId, Flow, LaneDef, LaneId, LaneSpeed, Mix, MixId, Modifier, ModifierKind, Order, PacingCurve,
    QueueEntry, Rules, SaveMix, SetOrders, SetQueue, SkillDef, SkillId, SourceId, StandingDef, StoreDef, StoreId,
    StoreValue, SwitchMix, TapCard, advance, decide, new_save, validate_rules,
)
from ashfall_app.engine import Save
from ashfall_app.engine.plan import running_mix_id

X = StoreId("x")
RACK = LaneId("rack")
H, R = CardId("h"), CardId("r")
ALWAYS = AfterTime(0)


def world(chips: tuple[ChipDef, ...] = (), standing: tuple[StandingDef, ...] = (), max_firings: int = 1000,
          cap: int | None = None) -> Rules:
    r = Rules(stores=(StoreDef(X, 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=standing,
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(RACK),),
              cards=(CardDef(H, 10, cap=cap), CardDef(R, 10, lane=RACK)), chips=chips,
              max_firings_per_instant=max_firings)
    validate_rules(r)
    return r


def running(s: Save, lane: LaneId) -> CardId | None:
    return next(ls.card for ls in s.lanes if ls.lane == lane)


def test_two_tap_orders_on_two_lanes_both_run_and_keep_running():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(R)), Order(ALWAYS, TapCard(H)))))
    assert (running(s, RACK), running(s, HANDS)) == (R, H)
    later = advance(s, r, 10)
    assert (running(later, RACK), running(later, HANDS)) == (R, H)


def test_a_tap_order_and_the_queues_head_both_act():
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(R)),)))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(H), AtLeast(CardCount(H), 3, 3)),)))
    assert (running(s, RACK), running(s, HANDS)) == (R, H)
    assert running(advance(s, r, 25), HANDS) == H


def test_a_tap_order_at_speed_zero_is_skipped_for_the_next():
    stopped = Modifier(LaneSpeed(RACK), ModifierKind.MUL_BP, 0, SourceId("still"))
    r = world()
    s = decide(new_save(r, (stopped,)), r, 0, SetOrders((Order(ALWAYS, TapCard(R)), Order(ALWAYS, TapCard(H)))))
    assert (running(s, RACK), running(s, HANDS)) == (None, H)


def test_a_chip_hiding_brings_a_skipped_tap_back():
    """While x is at most 1 the chip holds the hands at speed 0; the maker fills x, the chip hides, and the tap order
    starts at that instant, which nothing else evaluates."""
    maker = StandingDef(ActionId("maker"), makes=(Flow(X, 3600 * Q),))
    still = ChipDef(ChipId("still"), AtMost(StoreValue(X), Q, Q),
                    (Modifier(LaneSpeed(HANDS), ModifierKind.MUL_BP, 0, SourceId("still")),))
    r = world(chips=(still,), standing=(maker,))
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(H)),)))
    assert running(s, HANDS) is None and s.chips == (True,)
    t = next(t for t in range(1, 10) if not advance(s, r, t).chips[0])
    assert running(advance(s, r, t), HANDS) == H


def test_a_queued_switch_runs_at_a_pop_past_the_cap():
    """Two firings an instant: at 10, h's completion and landing reach the cap and the queue pops to its switch, whose
    mix runs at that instant: no verb waits on the cap."""
    m = MixId("m")
    r = world(max_firings=2, cap=5)
    s = decide(new_save(r), r, 0, SaveMix(Mix(m, (CardShare(H, BP),))))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(H), AtLeast(CardCount(H), 1, 1)),
                                  QueueEntry(SwitchMix(m), AtLeast(CardCount(H), 5, 5)))))
    assert running(s, HANDS) == H
    at = advance(s, r, 10)
    assert at.last_cascade is not None and at.last_cascade.time == 10 and at.active is None
    assert running_mix_id(at, r) == m
