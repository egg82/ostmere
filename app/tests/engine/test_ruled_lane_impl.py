"""A ruled lane (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS", "Ruled lane", "Lane order"): the
player never taps it, the queue never names it, rules drive it exactly as an unruled lane, and the view says which
rule's task it runs."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    HANDS, QUANTITY_SCALE as Q, AfterTime, AtLeast, CardCount, CardDef, CardId, InvalidVerbError, LaneDef, LaneId,
    Order, OrderState, PacingCurve, QueueEntry, Rules, Save, SetOrders, SetQueue, SkillDef, SkillId, StoreDef, StoreId,
    TapCard, advance, decide, new_save, validate_rules, view,
)

X = StoreId("x")
HELPER = LaneId("helper")
H, A, B = CardId("h"), CardId("a"), CardId("b")
ALWAYS = AfterTime(0)


def world(ruled: bool = True) -> Rules:
    r = Rules(stores=(StoreDef(X, 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(HELPER, ruled),),
              cards=(CardDef(H, 10), CardDef(A, 10, lane=HELPER), CardDef(B, 25, lane=HELPER)))
    validate_rules(r)
    return r


def test_the_player_never_taps_a_ruled_lane():
    r = world()
    with pytest.raises(InvalidVerbError, match="set by rules"):
        decide(new_save(r), r, 0, TapCard(A))
    assert decide(new_save(world(False)), world(False), 0, TapCard(A)).lanes[1].card == A   # control: unruled


def test_the_queue_never_names_a_ruled_lanes_card():
    r = world()
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, SetQueue((QueueEntry(TapCard(A), AtLeast(CardCount(A), 1, 1)),)))
    decide(new_save(r), r, 0, SetQueue((QueueEntry(TapCard(H), AtLeast(CardCount(H), 1, 1)),)))   # control


def test_rules_drive_a_ruled_lane_as_an_unruled_one():
    """Invariant 58: the same rules with ruled False give the same saves, but for the lane's flag."""
    orders = SetOrders((Order(AtLeast(CardCount(A), 2, 2), TapCard(B)), Order(ALWAYS, TapCard(A))))
    saves: list[list[Save]] = []
    for ruled in (True, False):
        r = world(ruled)
        s = decide(new_save(r), r, 0, orders)
        saves.append([advance(s, r, t) for t in (0, 10, 20, 45, 70, 100)])
    assert saves[0] == saves[1]
    assert [s.lanes[1].card for s in saves[0]] == [A, A, B, B, B, B]


def test_the_lane_bar_names_the_rule_whose_task_it_runs_and_later_rules_are_outranked():
    """Invariant 63: LaneBar.order is the first true, live rule tapping the running card; a later true rule on that
    lane is OUTRANKED, an earlier one that cannot act stays ON."""
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(AtLeast(CardCount(A), 1, 1), TapCard(B)), Order(ALWAYS, TapCard(A)),
                                             Order(ALWAYS, TapCard(B)), Order(ALWAYS, TapCard(H)))))
    v = view(s, r)
    bar = next(b for b in v.lanes if b.lane == HELPER)
    assert (bar.card, bar.order) == (A, 1)
    assert v.order_states == (OrderState.WAITING, OrderState.ON, OrderState.OUTRANKED, OrderState.ON)
    assert next(b for b in v.lanes if b.lane == HANDS).order == 3
    later = advance(s, r, 10)
    bar = next(b for b in view(later, r).lanes if b.lane == HELPER)
    assert (bar.card, bar.order) == (B, 0)
    assert view(later, r).order_states[1:3] == (OrderState.OUTRANKED, OrderState.OUTRANKED)


def test_a_lane_run_by_no_rule_has_no_order():
    r = world(False)
    s = decide(new_save(r), r, 0, TapCard(A))
    assert next(b for b in view(s, r).lanes if b.lane == HELPER).order is None
    s = decide(replace(s), r, 0, SetOrders((Order(ALWAYS, TapCard(B)),)))
    assert next(b for b in view(s, r).lanes if b.lane == HELPER).order is None   # it runs a, not b
