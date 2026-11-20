"""Invariant 181 and the choices on joins and marks (engine DESIGN.txt, "GROUPS (pooled lanes)", "Join", "Mark")."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, CardShare, Join, Leave, Mark, Mix, Order, Outcome, SetOrders, TapCard, TriggerDef, TriggerId, Unlock,
    LaneBar, LaneId, Save, UnlockKind, advance, decide, view,
)
from tests.kills import kills
from groups_world import (
    ALWAYS, GA, GB, P1, P2, P3, TOWN, X, Y, card_view, crew_triggers, join, lane_state, mark, own, split_mix, start, stored, world,
)

SPLIT = ((GA, 5000), (own(P1, "a"), 6000), (own(P1, "b"), 4000))


def _unmarked_pair(*extra: TriggerDef):
    """P1 joined marked with its own split, P2 joined unmarked, both in the town mix."""
    r = world((join(P1, own(P1, "a"), True), join(P2, GA, False), *extra))
    return r, start(r, split_mix(*SPLIT))


def _core(s: Save) -> Save:
    """A save but for what a mark's latch and lane state may differ in (the trigger bookkeeping)."""
    return replace(s, lanes=(), fired=(), latches=())


def test_181_clearing_then_setting_in_one_instant_gives_the_save_it_started_from():
    clear_set = (mark(P1, False, at=10, tid="m1"), mark(P1, True, at=10, tid="m2"))
    r, s = _unmarked_pair(*clear_set)
    r0, s0 = _unmarked_pair()
    a, b = advance(s, r, 10), advance(s0, r0, 10)
    assert _core(a) == _core(b)
    assert lane_state(a, P1) == lane_state(b, P1)
    assert stored(s, r, X, 500) == stored(s0, r0, X, 500) and stored(s, r, Y, 500) == stored(s0, r0, Y, 500)


@kills(13)
def test_181_a_mark_change_never_changes_a_share():
    r, s = _unmarked_pair(mark(P1, False, at=10), mark(P1, True, at=30))
    before = s.mixes
    assert advance(s, r, 9).mixes == before
    assert advance(s, r, 20).mixes == before
    assert advance(s, r, 40).mixes == before


def test_181_the_split_a_person_had_comes_back_when_they_are_marked_again():
    r, s = _unmarked_pair(mark(P1, False, at=10), mark(P1, True, at=30))
    r0, s0 = _unmarked_pair()
    assert stored(s, r, X, 20) - stored(s, r, X, 10) < stored(s0, r0, X, 20) - stored(s0, r0, X, 10)
    gap = stored(s0, r0, X, 30) - stored(s, r, X, 30)
    assert gap > 0
    assert stored(s0, r0, X, 100) - stored(s, r, X, 100) == gap
    assert stored(s, r, Y, 100) < stored(s0, r0, Y, 100)
    assert stored(s0, r0, Y, 100) - stored(s, r, Y, 100) == stored(s0, r0, Y, 30) - stored(s, r, Y, 30)


def test_181_an_unmarked_persons_own_shares_are_idle_while_the_mark_is_clear():
    r, s = _unmarked_pair(mark(P1, False, at=10))
    def own_y(t: int):
        return card_view(s, r, own(P1, "b"), t).bar

    assert own_y(9).rate > 0 and own_y(11).rate == 0
    assert any(c == CardShare(own(P1, "b"), 4000) for m in advance(s, r, 50).mixes for c in m.components)


# ---- the mark ---------------------------------------------------------------------------------------------------------

def test_mark_clears_and_sets_the_lane_state_and_the_view():
    r, s = _unmarked_pair(mark(P1, False, at=10), mark(P1, True, at=30))
    def bar(t: int, lane: LaneId) -> LaneBar:
        return next(b for b in view(advance(s, r, t), r).lanes if b.lane == lane)

    assert lane_state(advance(s, r, 9), P1).own_split and bar(9, P1).own_split is True
    assert lane_state(advance(s, r, 10), P1).own_split is False and bar(10, P1).own_split is False
    assert lane_state(advance(s, r, 30), P1).own_split and bar(30, P1).own_split is True
    assert bar(10, P2).own_split is False


def test_mark_with_a_card_adds_a_whole_share_when_the_town_mix_holds_none_of_theirs():
    r = world((join(P1, GA, False), join(P2, own(P2, "a"), True), mark(P1, True, own(P1, "a"), at=10)))
    s = advance(start(r, split_mix((GA, BP), (own(P2, "a"), BP))), r, 10)
    assert CardShare(own(P1, "a"), BP) in s.mixes[0].components
    assert lane_state(s, P1).own_split


def test_mark_with_a_card_adds_nothing_when_the_town_mix_holds_a_share_of_theirs():
    r = world((join(P1, GA, False), join(P2, own(P2, "a"), True), mark(P1, True, own(P1, "a"), at=10)))
    own_b = CardShare(own(P1, "b"), 3000)
    s0 = start(r, split_mix((GA, BP), (own(P2, "a"), BP), (own(P1, "b"), 3000)))
    s = advance(s0, r, 10)
    assert s.mixes == s0.mixes and own_b in s.mixes[0].components


def test_mark_lands_after_joins_in_one_outcome():
    t = TriggerDef(TriggerId("both"), AfterTime(0), Outcome(joins=(Join(P1, TOWN, own(P1, "a"), True),), marks=(Mark(P1, False),)))
    r = world((t,))
    s = start(r)
    assert Unlock(UnlockKind.JOINED, P1) in s.unlocked and not lane_state(s, P1).own_split


def test_mark_on_a_lane_not_joined_changes_nothing():
    r = world((join(P1, GA, False), mark(P2, False, at=10), mark(P3, True, own(P3, "a"), at=10)))
    r0 = world((join(P1, GA, False),))
    a, b = advance(start(r), r, 20), advance(start(r0), r0, 20)
    assert (a.mixes, a.orders, a.unlocked, a.stores) == (b.mixes, b.orders, b.unlocked, b.stores)
    assert all(lane_state(a, p).own_split for p in (P2, P3))


def test_mark_on_a_left_lane_changes_nothing():
    leave = TriggerDef(TriggerId("gone"), AfterTime(5), Outcome(leaves=(Leave(P1),)))
    r = world((join(P1, GA, False), join(P2, GA, False), leave, mark(P1, True, own(P1, "a"), at=10)))
    r0 = world((join(P1, GA, False), join(P2, GA, False), leave))
    a, b = advance(start(r), r, 20), advance(start(r0), r0, 20)
    assert (a.mixes, a.orders, a.unlocked) == (b.mixes, b.orders, b.unlocked)
    assert lane_state(a, P1) == lane_state(b, P1)


def test_mark_with_no_crew_left_idles_the_group_card():
    r, s = _unmarked_pair(mark(P2, True, at=10))
    assert stored(s, r, X, 500) - stored(s, r, X, 10) == Q * 6 * 49
    assert card_view(s, r, GA, 20).crew == 0 and card_view(s, r, GA, 9).crew == 1


# ---- the join ---------------------------------------------------------------------------------------------------------

def test_an_unmarked_join_starts_the_group_at_a_whole_split_with_the_joins_card():
    r = world((join(P1, GA, False),))
    s = start(r)
    assert s.mixes == (Mix(TOWN, (CardShare(GA, BP),), s.mixes[0].layer),)
    assert not lane_state(s, P1).own_split and Unlock(UnlockKind.JOINED, P1) in s.unlocked


def test_a_later_member_adds_output_under_the_split_already_set():
    r = world(crew_triggers(1) + (join(P2, GB, False, at=10),))
    s = start(r, split_mix((GA, 3000), (GB, 2000)))
    s = advance(s, r, 10)
    assert s.mixes[0].components == (CardShare(GA, 3000), CardShare(GB, 2000))
    assert card_view(s, r, GA, 11).crew == 2 and card_view(s, r, GB, 11).crew == 2


def test_an_unmarked_join_gives_the_share_to_the_group_even_when_the_card_is_not_the_first():
    r = world((join(P1, own(P1, "a"), True), join(P2, GA, False)))
    s = start(r)
    comps = s.mixes[0].components
    assert CardShare(own(P1, "a"), BP) in comps and CardShare(GA, BP) in comps and len(comps) == 2


def test_an_unmarked_join_adds_no_share_when_the_town_mix_holds_one_of_a_card_on_the_group():
    r = world((join(P1, GA, False), join(P2, GA, False, at=10)))
    s = start(r, split_mix((GB, 2500)))
    assert advance(s, r, 10).mixes[0].components == (CardShare(GB, 2500),)


def test_an_unmarked_join_removes_the_lanes_uncapped_always_rule_still():
    r = world((join(P1, GA, False, at=10),))
    s = decide(start(r), r, 0, SetOrders((Order(ALWAYS, TapCard(own(P1, "a"))),)))
    a = advance(s, r, 10)
    assert all(not (isinstance(o.then, TapCard) and o.then.card == own(P1, "a")) for o in a.orders)
    assert lane_state(a, P1).card is None


def test_a_marked_join_keeps_what_every_released_join_meant():
    r = world((join(P1, own(P1, "a"), True),))
    plain = replace(r, triggers=(TriggerDef(TriggerId("join-p1"), ALWAYS, Outcome(joins=(Join(P1, TOWN, own(P1, "a")),))),))
    a, b = start(r), start(plain)
    assert a == b and lane_state(a, P1).own_split
    assert CardShare(own(P1, "a"), BP) in a.mixes[0].components
