"""Invariants 179 and 180 (engine DESIGN.txt, "GROUPS (pooled lanes)"): crew equals people, and a tap takes one member."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, CardShare, Rules, RunKind, Save, advance, view,
)
from tests.kills import kills
from groups_world import (
    GA, GB, OFF_S, P1, P2, P3, PEOPLE, Q1, X, Y, card_view, crew_triggers, join, lane_state, own, save_mix, split_mix, start,
    stored, tap_order, tap_orders, work, world,
)

SPLIT = ((GA, 4000), (GB, 3000))


def _group(k: int):
    r = world(crew_triggers(k))
    return r, start(r, split_mix(*SPLIT))


def _people(k: int):
    """k marked people, each running SPLIT on their own cards."""
    r = world(tuple(join(p, own(p, "a"), True) for p in PEOPLE[:k]))
    shares = tuple(CardShare(own(p, w), bp) for p in PEOPLE[:k] for w, bp in (("a", 4000), ("b", 3000)))
    return r, start(r, save_mix(shares))




def _crew_work(s: Save, r: Rules, k: int, t: int, w: str) -> int:
    return sum(work(s, r, own(p, w), t) for p in PEOPLE[:k])


@kills(11)
@given(k=st.integers(1, 3), t=st.integers(0, 3000))
def test_179_crew_equals_people_stores_and_work(k: int, t: int):
    gr, gs = _group(k)
    pr, ps = _people(k)
    for store in (X, Y):
        assert stored(gs, gr, store, t) == stored(ps, pr, store, t)
    assert work(gs, gr, GA, t) == _crew_work(ps, pr, k, t, "a")
    assert work(gs, gr, GB, t) == _crew_work(ps, pr, k, t, "b")


@given(k=st.integers(1, 3), cuts=st.lists(st.integers(1, 500), min_size=1, max_size=5))
def test_179_crew_equals_people_at_any_slicing(k: int, cuts: list[int]):
    gr, gs = _group(k)
    pr, ps = _people(k)
    t = 0
    for c in cuts:
        t += c
        gs, ps = advance(gs, gr, t), advance(ps, pr, t)
        view(gs, gr)
        assert stored(gs, gr, X, t) == stored(ps, pr, X, t) and stored(gs, gr, Y, t) == stored(ps, pr, Y, t)
        assert work(gs, gr, GA, t) == _crew_work(ps, pr, k, t, "a")


@kills(15)
def test_179_a_marked_person_adds_nothing_to_the_group():
    """Two unmarked members and one marked person running SPLIT on their own cards equal three marked people."""
    r = world((join(P1, GA, False), join(P2, GA, False), join(P3, own(P3, "a"), True)))
    shares = (*(CardShare(c, bp) for c, bp in SPLIT), CardShare(own(P3, "a"), 4000), CardShare(own(P3, "b"), 3000))
    s = start(r, save_mix(shares))
    pr, ps = _people(3)
    for t in (7, 100, 2000):
        assert stored(s, r, X, t) == stored(ps, pr, X, t) and stored(s, r, Y, t) == stored(ps, pr, Y, t)


def test_179_an_unmarked_persons_own_shares_stay_in_the_mix_and_do_nothing():
    r = world((join(P1, GA, False), join(P2, GA, False)))
    plain = start(r, split_mix(*SPLIT))
    kept = start(r, save_mix((*(CardShare(c, bp) for c, bp in SPLIT), CardShare(own(P1, "a"), BP))))
    assert any(isinstance(c, CardShare) and c.card == own(P1, "a") for m in kept.mixes for c in m.components)
    for t in (50, 1000):
        assert stored(kept, r, X, t) == stored(plain, r, X, t)
        assert work(kept, r, own(P1, "a"), t) == 0


def test_179_the_crew_is_the_members_not_the_headcount_of_people_without_a_mark():
    """P3 is in G's lane group but has not joined, and P2 joined marked: only the unmarked joined count."""
    r = world((join(P1, GA, False), join(P2, own(P2, "a"), True)))
    s = start(r, split_mix((GA, BP)))
    assert card_view(s, r, GA, 10).crew == 1
    assert stored(s, r, X, 10) == 10 * Q


def test_179_a_member_who_has_not_joined_is_not_in_the_crew():
    r = world((join(P1, GA, False), join(P2, GA, False, at=100)))
    s = start(r, split_mix((GA, BP)))
    assert stored(s, r, X, 100) == 100 * Q
    assert stored(s, r, X, 300) == 100 * Q + 200 * 2 * Q


# ---- 180 --------------------------------------------------------------------------------------------------------------

T0 = 30


def _member_seconds(k: int, t: int) -> int:
    """Member-seconds a group card at a whole split has by t with k members, one tapped from T0 for OFF_S seconds."""
    return k * t - max(0, min(t, T0 + OFF_S) - T0)


def _tapped(k: int):
    r = world(crew_triggers(k))
    s = start(r, split_mix((GA, BP)), tap_order(T0, P1))
    return r, s


@kills(12)
@given(k=st.integers(1, 3), t=st.integers(0, 200))
def test_180_a_tap_on_one_member_lowers_the_group_to_k_minus_1_over_k(k: int, t: int):
    r, s = _tapped(k)
    assert stored(s, r, X, t) == Q * _member_seconds(k, t)


@given(k=st.integers(1, 3), t=st.integers(0, 200))
def test_180_the_group_cards_work_follows_the_same_crew(k: int, t: int):
    r, s = _tapped(k)
    assert work(s, r, GA, t) == BP * _member_seconds(k, t)


def test_180_the_crew_shown_drops_and_is_restored_at_the_landing():
    r, s = _tapped(3)
    assert card_view(s, r, GA, T0 - 1).crew == 3
    assert card_view(s, r, GA, T0 + 1).crew == 2
    assert card_view(s, r, GA, T0 + OFF_S - 1).crew == 2
    assert card_view(s, r, GA, T0 + OFF_S).crew == 3


def test_180_no_other_lane_changes():
    """A marked person on no group (Q1), and the other two members, are as they are with no tap."""
    triggers = (*crew_triggers(3), join(Q1, own(Q1, "b"), True))
    r = world(triggers)
    mix = split_mix((GA, BP), (own(Q1, "b"), BP))
    tapped = start(r, mix, tap_order(T0, P1))
    free = start(r, mix)
    for t in (T0 + 5, T0 + OFF_S + 5, 200):
        a, b = advance(tapped, r, t), advance(free, r, t)
        assert stored(tapped, r, Y, t) == stored(free, r, Y, t)
        assert work(tapped, r, own(Q1, "b"), t) == work(free, r, own(Q1, "b"), t)
        for lane in (P2, P3, Q1):
            assert lane_state(a, lane) == lane_state(b, lane)
        assert work(tapped, r, own(P2, "a"), t) == 0 == work(tapped, r, own(P3, "a"), t)
    assert lane_state(advance(tapped, r, T0 + 5), P1).card == own(P1, "off")


def test_180_every_member_tapped_leaves_the_group_card_yielded_with_no_crew():
    r = world(crew_triggers(2))
    s = start(r, split_mix((GA, BP)), tap_orders((T0, P1), (T0, P2)))
    cv = card_view(s, r, GA, T0 + 5)
    assert cv.crew == 0 and cv.run is RunKind.YIELDED and cv.share_bp == BP
    assert stored(s, r, X, T0 + OFF_S) == stored(s, r, X, T0 + 1)
    assert card_view(s, r, GA, T0 + OFF_S).crew == 2
