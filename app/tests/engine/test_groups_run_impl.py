"""Groups run (engine DESIGN.txt, "GROUPS (pooled lanes)", "How a group's split runs", "Join", "Mark"): the first
member starts the group's split, a later one adds output under it, a mark moves a person between their own split and
the group's and never touches a share, and a tap on a member takes that person from the crew."""
import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, CardDef, CardId, CardShare, Flow, InvalidVerbError, Join, LaneDef, LaneId, Mark,
    Mix, MixId, Order, Outcome, PacingCurve, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, StoreDef, StoreId,
    TapCard, TriggerDef, TriggerId, advance, decide, new_save, validate_rules, value, view,
)

X = StoreId("x")
G, P1, P2, P3 = LaneId("g"), LaneId("p1"), LaneId("p2"), LaneId("p3")
GWORK, A1, A2, ONE = CardId("gwork"), CardId("a1"), CardId("a2"), CardId("one")
TOWN = MixId("town:main")
HOUR = 3600


def world(*steps: tuple[int, Outcome]) -> Rules:
    """Pooled g with one card; p1, p2 in group g, p3 with none, each with a card of their own at the same pace; p1
    also has a one-off. Each step is a trigger at its time."""
    cards = (CardDef(GWORK, 100, lane=G, makes=(Flow(X, Q),)), CardDef(A1, 100, lane=P1, makes=(Flow(X, Q),)),
             CardDef(A2, 100, lane=P2, makes=(Flow(X, Q),)), CardDef(CardId("a3"), 100, lane=P3, makes=(Flow(X, Q),)),
             CardDef(ONE, 500, lane=P1, cap=1))
    r = Rules(stores=(StoreDef(X, 10**9 * Q, 0),), skills=(), standing=(), curve=PacingCurve((10**9 * Q,)),
              lanes=(LaneDef(G, True, pooled=True), LaneDef(P1, True, group=G), LaneDef(P2, True, group=G),
                     LaneDef(P3, True)),
              cards=cards, triggers=tuple(TriggerDef(TriggerId(f"t{i}"), AfterTime(t), o) for i, (t, o) in enumerate(steps)))
    validate_rules(r)
    return r


def rate(s: Save, r: Rules) -> int:
    """Store x per second over the minute after s, which holds no event."""
    return (value(s, r, X, s.time + 60) - value(s, r, X, s.time)) // 60


def share_cards(s: Save) -> list[tuple[str, int]]:
    return [(c.card, c.share_bp) for m in s.mixes for c in m.components if isinstance(c, CardShare)]


def crew(s: Save, r: Rules) -> int | None:
    return next(c for c in view(s, r).cards if c.card == GWORK).crew


def at(r: Rules, t: int) -> Save:
    return advance(new_save(r), r, t)


def unmarked(lane: LaneId, card: CardId = GWORK, t: int = 1) -> tuple[int, Outcome]:
    return t, Outcome(joins=(Join(lane, TOWN, card, own_split=False),))


def own(lane: LaneId, card: CardId, t: int = 1) -> tuple[int, Outcome]:
    return t, Outcome(joins=(Join(lane, TOWN, card),))


UNIT = rate(at(world(own(P3, CardId("a3"))), 500), world(own(P3, CardId("a3"))))


def test_a_lone_person_runs_at_a_unit_rate():
    """The yardstick the others are counted in: it is above 0."""
    assert UNIT > 0


def test_the_first_member_starts_the_group_at_a_whole_split_and_nothing_goes_to_their_own_lane():
    r = world(unmarked(P1))
    s = at(r, 500)
    assert share_cards(s) == [(GWORK, 10000)]
    assert [ls.own_split for ls in s.lanes if ls.lane == P1] == [False]
    assert rate(s, r) == UNIT
    assert crew(s, r) == 1


def test_a_second_member_adds_output_under_the_split_already_set():
    r = world(unmarked(P1), unmarked(P2, t=2))
    s = at(r, 500)
    assert share_cards(s) == [(GWORK, 10000)]
    assert rate(s, r) == 2 * UNIT
    assert crew(s, r) == 2


def test_a_marked_person_adds_nothing_to_the_group_and_runs_their_own_split():
    r = world(unmarked(P1), own(P3, CardId("a3"), t=2))
    s = at(r, 500)
    assert rate(s, r) == 2 * UNIT
    assert crew(s, r) == 1


def test_a_group_with_no_members_accepts_a_split_that_runs_nothing_and_shows_no_crew():
    """A SaveMix of a card on a pooled lane is valid whether or not the group has members (the split idles)."""
    r = world(own(P3, CardId("a3")))
    s = decide(at(r, 500), r, 500, SaveMix(Mix(TOWN, (CardShare(CardId("a3"), 10000), CardShare(GWORK, 10000)))))
    assert share_cards(s) == [(CardId("a3"), 10000), (GWORK, 10000)]
    assert (rate(s, r), crew(s, r)) == (UNIT, 0)


def test_a_mark_moves_a_person_between_the_group_and_their_own_split_and_changes_no_share():
    r = world(own(P1, A1), unmarked(P2), (1000, Outcome(marks=(Mark(P1, False),))),
              (2000, Outcome(marks=(Mark(P1, True),))))
    before, unmarked_p1, remarked = at(r, 500), at(r, 1500), at(r, 2500)
    assert share_cards(before) == share_cards(unmarked_p1) == share_cards(remarked) == [(A1, 10000), (GWORK, 10000)]
    assert (rate(before, r), crew(before, r)) == (2 * UNIT, 1)
    assert (rate(unmarked_p1, r), crew(unmarked_p1, r)) == (2 * UNIT, 2)
    assert (rate(remarked, r), crew(remarked, r)) == (2 * UNIT, 1)
    assert [ls.own_split for ls in unmarked_p1.lanes if ls.lane == P1] == [False]
    assert [ls.own_split for ls in remarked.lanes if ls.lane == P1] == [True]


def test_marking_a_person_with_no_share_gives_them_the_marks_card():
    r = world(unmarked(P1), (1000, Outcome(marks=(Mark(P1, True, A1),))))
    s = at(r, 1500)
    assert share_cards(s) == [(GWORK, 10000), (A1, 10000)]
    assert (rate(s, r), crew(s, r)) == (UNIT, 0)


def test_unmarking_a_person_with_the_groups_card_starts_the_group_at_a_whole_split():
    r = world(own(P1, A1), own(P2, A2), (1000, Outcome(marks=(Mark(P1, False, GWORK), Mark(P2, False, GWORK)))))
    s = at(r, 1500)
    assert share_cards(s) == [(A1, 10000), (A2, 10000), (GWORK, 10000)]
    assert (rate(s, r), crew(s, r)) == (2 * UNIT, 2)


def test_unmarking_adds_no_share_when_the_group_already_has_one():
    r = world(unmarked(P1), own(P2, A2), (1000, Outcome(marks=(Mark(P2, False, GWORK),))))
    assert share_cards(at(r, 1500)).count((GWORK, 10000)) == 1


def test_an_unmarking_card_is_one_on_the_persons_group():
    with pytest.raises(Exception, match="not an uncapped card on its group"):
        world(own(P1, A1), (1000, Outcome(marks=(Mark(P1, False, A1),))))


def test_a_mark_on_a_person_not_joined_changes_nothing():
    r = world((1000, Outcome(marks=(Mark(P1, False),))))
    assert at(r, 1500).mixes == ()
    assert [ls.own_split for ls in at(r, 1500).lanes if ls.lane == P1] == [True]


def test_a_tap_on_a_member_takes_them_from_the_crew_and_keeps_their_mark():
    r = world(unmarked(P1), unmarked(P2, t=2), (1000, Outcome(starts=(ONE,))))
    during = at(r, 1100)
    assert crew(during, r) == 1
    assert rate(during, r) == UNIT
    after = at(r, 1700)
    assert crew(after, r) == 2
    assert rate(after, r) == 2 * UNIT
    assert [ls.own_split for ls in after.lanes if ls.lane == P1] == [False]


def test_the_lane_bar_shows_a_persons_mark_and_no_other_lane_a_mark():
    r = world(own(P1, A1), unmarked(P2))
    marks = {b.lane: b.own_split for b in view(at(r, 5), r).lanes}
    assert marks == {"hands": None, G: None, P1: True, P2: False, P3: True}


def test_the_player_cannot_plan_a_tap_of_a_pooled_card_but_can_split_one():
    r = world(unmarked(P1))
    s = at(r, 5)
    for verb in (TapCard(GWORK), SetOrders((Order(AfterTime(0), TapCard(GWORK)),)),
                 SetQueue((QueueEntry(TapCard(GWORK), AfterTime(0)),))):
        with pytest.raises(InvalidVerbError):
            decide(s, r, 5, verb)
    capped = Mix(TOWN, (CardShare(GWORK, 6000), CardShare(GWORK, 6000)))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 5, SaveMix(capped))
    assert share_cards(decide(s, r, 5, SaveMix(Mix(TOWN, (CardShare(GWORK, 6000),))))) == [(GWORK, 6000)]
