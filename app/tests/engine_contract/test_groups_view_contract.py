"""The choices of "GROUPS (pooled lanes)" that no numbered invariant states: the group card's view, a group's speed, and
the verbs' plan checks."""
from collections.abc import Callable

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, CardShare, HANDS, InvalidVerbError, Modifier, ModifierKind, LaneSpeed, Order, Outcome, QueueEntry,
    LaneId, RunKind, SetOrders, SetQueue, SourceId, TapCard, TriggerDef, TriggerId, Verb, decide, view,
)
from tests.kills import kills
from groups_world import (
    ALWAYS, G, GA, GB, P1, P2, X, card_view, crew_triggers, join, own, split_mix, start, stored, world,
)


def test_a_group_card_shows_its_crew_and_the_totals_over_the_free_members():
    r = world(crew_triggers(3))
    s = start(r, split_mix((GA, 4000)))
    cv = card_view(s, r, GA, 10)
    assert cv.crew == 3 and cv.share_bp == 12000 and cv.run is RunKind.FULL


def test_the_crew_is_none_on_a_card_of_no_pooled_lane():
    r = world((join(P1, own(P1, "a"), True),))
    s = start(r)
    assert card_view(s, r, own(P1, "a"), 10).crew is None


@kills(10)
def test_the_lane_bar_shows_the_mark_on_person_lanes_only():
    r = world((join(P1, GA, False), join(P2, own(P2, "a"), True)))
    bars = {b.lane: b for b in view(start(r), r).lanes}
    assert bars[P1].own_split is False and bars[P2].own_split is True
    assert G not in bars or bars[G].own_split is None
    assert bars[HANDS].own_split is None


# ---- speed ------------------------------------------------------------------------------------------------------------

def _slow(lane: LaneId, bp: int) -> TriggerDef:
    return TriggerDef(TriggerId(f"slow-{lane}"), ALWAYS,
                      Outcome(modifiers=(Modifier(LaneSpeed(lane), ModifierKind.MUL_BP, bp, SourceId("slow")),)))


def test_a_group_card_runs_at_the_pooled_lanes_speed():
    r = world((*crew_triggers(2), _slow(G, 5000)))
    s = start(r, split_mix((GA, BP)))
    assert stored(s, r, X, 100) == 2 * 100 * Q // 2


@kills(14)
def test_a_members_speed_never_reaches_a_group_card_but_reaches_their_own():
    r = world((*crew_triggers(2), _slow(P1, 5000)))
    s = start(r, split_mix((GA, BP)))
    assert stored(s, r, X, 100) == 2 * 100 * Q


# ---- verbs ------------------------------------------------------------------------------------------------------------

def _town():
    r = world((join(P1, own(P1, "a"), True),))
    return r, start(r)


def test_a_group_cards_shares_in_a_town_mix_sum_to_at_most_a_whole_split():
    r, s = _town()
    decide(s, r, 0, split_mix((GA, 6000), (GB, 4000)))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, split_mix((GA, 6000), (GB, 4001)))


def test_a_group_card_is_accepted_in_a_town_mix_whether_or_not_the_group_has_members():
    r, s = _town()
    out = decide(s, r, 0, split_mix((GA, BP)))
    assert out.mixes[0].components[0] == CardShare(GA, BP)


@pytest.mark.parametrize("verb", [
    lambda: SetOrders((Order(ALWAYS, TapCard(GA)),)),
    lambda: SetQueue((QueueEntry(TapCard(GA), AfterTime(10)),)),
    lambda: TapCard(GA),
], ids=["orders", "queue", "tap"])
def test_a_tap_of_a_group_card_is_refused(verb: Callable[[], Verb]):
    r, s = _town()
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, verb())
