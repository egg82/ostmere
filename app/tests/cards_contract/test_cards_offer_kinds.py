"""The kind's answer verb AnswerKind (engine DESIGN.txt, "OFFER KINDS", invariants 98-105). Written from the interface
text only. Each test names its invariant; the bodies exercise the engine's public entry points on town_world's world
with kind_world's offers (one, two, three of the arrival kind, two listing its answers the other way round; stranger of
another kind with the same role names; ask with no kind)."""
from collections.abc import Sequence

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerDef, AnswerId, AnswerOffer, InvalidRulesError, InvalidVerbError, Line, OfferDef, Order,
    OrderState, QueueEntry, Rules, Save, SetOrders, SetQueue, advance, advance_logged, decide, decide_logged, decode,
    encode, new_save, view,
)
from cards_world import keys
from kind_world import (
    ARRIVAL, ONE, ONE_T, ONE_W, STR_T, STR_W, STRANGER, STRANGER_KIND, THREE, THREE_T, THREE_W, TURN_AWAY, TWO, TWO_T,
    TWO_W, WELCOME, RoleId, KindId, answer_def, kinded, rule, world,
)
from town_world import ASK, NEVER, NO, YES, answered, given, shown, started, town

ON = Order(AfterTime(0), rule())
"""The welcome rule for the arrival kind, always true."""


def armed(r: Rules, *extra: Order) -> Save:
    return started(r, SetOrders((ON,) + extra))


def said(lines: Sequence[Line]) -> list[tuple[int, str]]:
    return [(t, k) for t, k in keys(lines) if k.endswith(".said")]


# ---- 98 answer both ways ------------------------------------------------------------------------------------------

def test_98_the_rule_answers_an_open_offer_with_its_role():
    """98: one open offer of the kind: answered at the instant it shows, with the answer holding the rule's role; a
    rule for the other role gives the other answer."""
    r = world(one=50)
    s = advance(armed(r), r, 49)
    assert not shown(s, ONE) and not answered(s, ONE)
    s = advance(s, r, 50)
    assert answered(s, ONE) and given(s, ONE_W) and not given(s, ONE_T)
    t = advance(started(r, SetOrders((Order(AfterTime(0), rule(role=TURN_AWAY)),))), r, 50)
    assert given(t, ONE_T) and not given(t, ONE_W)


def test_98_the_answer_lands_its_outcome_and_both_unlocks_as_the_players_would():
    """98, the AnswerOffer semantics: ANSWERED and ANSWER enter together and the answer's line is in the step at the
    instant the offer shows."""
    r = world(one=50)
    step = advance_logged(armed(r), r, 60)
    assert answered(step.save, ONE) and given(step.save, ONE_W)
    assert said(step.lines) == [(50, f"{ONE_W}.said")]


def test_98_the_rule_equals_the_players_answers_at_each_instant():
    """98 (invariant 62's shape): the rule set before one (50) and two (200) show gives the stores, cards, lanes,
    unlocked, modifiers and fired of the player's AnswerOffer(one, one_w) at 50 and AnswerOffer(two, two_w) at 200, the
    same lines in the same order, and orders that differ only by the rule."""
    r = world(one=50, two=200)
    ruled = advance_logged(armed(r), r, 300)
    first = decide_logged(advance(started(r), r, 50), r, 50, AnswerOffer(ONE, ONE_W))
    mid = advance_logged(first.save, r, 200)
    last = decide_logged(mid.save, r, 200, AnswerOffer(TWO, TWO_W))
    x, y = advance(last.save, r, 300), ruled.save
    assert given(x, ONE_W) and given(x, TWO_W)
    assert (x.stores, x.cards, x.lanes, x.unlocked, x.modifiers, x.fired) == \
        (y.stores, y.cards, y.lanes, y.unlocked, y.modifiers, y.fired)
    assert ON in y.orders and ON not in x.orders and [o for o in y.orders if o != ON] == list(x.orders)
    assert said(ruled.lines) == said(first.lines + mid.lines + last.lines) == \
        [(50, f"{ONE_W}.said"), (200, f"{TWO_W}.said")]


def test_98_two_open_offers_are_answered_by_the_one_decision_that_sets_the_rule():
    """98, 'then ... AnswerOffer(on, an) at T': one and three open together, the rule set: both answered at that instant
    (evaluation runs on after the first answer)."""
    r = world(one=50, three=50)
    s = advance(started(r), r, 60)
    assert shown(s, ONE) and shown(s, THREE) and not answered(s, ONE) and not answered(s, THREE)
    step = decide_logged(s, r, 60, SetOrders((ON,)))
    t = step.save
    assert given(t, ONE_W) and given(t, THREE_W) and not given(t, ONE_T) and not given(t, THREE_T)
    assert said(step.lines) == [(60, f"{ONE_W}.said"), (60, f"{THREE_W}.said")]


# ---- 99 second at the instant it shows ----------------------------------------------------------------------------

def test_99_a_later_offer_is_answered_at_the_second_it_shows_and_the_rule_stays():
    """99: one shows at 50 and is answered, two shows at 200 and is answered at 200 (not at a later visit); the rule is
    still in save.orders."""
    r = world(one=50, two=200)
    s = advance(armed(r), r, 199)
    assert answered(s, ONE) and not shown(s, TWO) and not answered(s, TWO)
    step = advance_logged(s, r, 200)
    assert given(step.save, TWO_W) and said(step.lines) == [(200, f"{TWO_W}.said")] and ON in step.save.orders
    assert given(advance(armed(r), r, 10**6), TWO_W)


def test_99_an_offer_shown_while_another_is_open_is_answered_at_its_instant_too():
    """99, 'whether or not an earlier offer of k was open': one and two both show at 50 with the rule held; three shows
    at 80 while nothing is open; all three are answered, each at its own instant."""
    r = world(one=50, two=50, three=80)
    step = advance_logged(armed(r), r, 100)
    assert said(step.lines) == [(50, f"{ONE_W}.said"), (50, f"{TWO_W}.said"), (80, f"{THREE_W}.said")]


# ---- 100 open only ------------------------------------------------------------------------------------------------

def test_100_an_offer_of_another_kind_and_an_unkinded_offer_are_left_open():
    """100: stranger (another kind, the same role names) and ask (no kind) are shown and stay open under the arrival
    rule while one is answered."""
    r = world(one=50, stranger=50, ask=50)
    s = advance(armed(r), r, 100)
    assert answered(s, ONE)
    for o, answers in ((STRANGER, (STR_W, STR_T)), (ASK, (YES, NO))):
        assert shown(s, o) and not answered(s, o) and not any(given(s, a) for a in answers)


def test_100_the_other_kinds_rule_answers_only_the_other_kind():
    """100, the converse control: a stranger-kind rule answers stranger and leaves one open, so a rule acting on every
    kinded offer would fail the test above and this one."""
    r = world(one=50, stranger=50)
    s = advance(started(r, SetOrders((Order(AfterTime(0), rule(STRANGER_KIND)),))), r, 100)
    assert given(s, STR_W) and not answered(s, ONE)


def test_100_an_offer_not_yet_shown_is_not_answered():
    """100: the rule held while one is not shown writes nothing (no ANSWERED, ANSWER or line); the offer is still open for
    the player when it shows."""
    r = world(one=500)
    step = advance_logged(armed(r), r, 499)
    s = step.save
    assert not shown(s, ONE) and not answered(s, ONE) and not given(s, ONE_W) and not given(s, ONE_T)
    assert said(step.lines) == []
    s = advance(decide(s, r, 499, SetOrders(())), r, 600)
    assert shown(s, ONE) and not answered(s, ONE)
    assert given(decide(s, r, 600, AnswerOffer(ONE, ONE_T)), ONE_T)


def test_100_an_answered_offer_is_not_answered_again():
    """100: an offer the player answered the other way keeps its answer when the rule is set."""
    r = world(one=50)
    s = decide(advance(started(r), r, 60), r, 60, AnswerOffer(ONE, ONE_T))
    s = decide(s, r, 60, SetOrders((ON,)))
    assert given(s, ONE_T) and not given(s, ONE_W)


def test_100_with_no_open_offer_a_true_order_changes_nothing():
    """100: no offer shown, the rule true: the save after an advance differs from the save without the rule only by its
    orders."""
    r = world(one=500)
    with_rule, without = advance(armed(r), r, 300), advance(started(r), r, 300)
    assert (with_rule.stores, with_rule.cards, with_rule.lanes, with_rule.unlocked, with_rule.fired) == \
        (without.stores, without.cards, without.lanes, without.unlocked, without.fired)


# ---- 101 by role --------------------------------------------------------------------------------------------------

def test_101_roles_match_by_role_whatever_the_answers_order():
    """101: two lists its turn_away answer first; the welcome rule still gives two_w and the turn_away rule two_t."""
    r = world(two=50)
    s = advance(armed(r), r, 50)
    assert given(s, TWO_W) and not given(s, TWO_T)
    t = advance(started(r, SetOrders((Order(AfterTime(0), rule(role=TURN_AWAY)),))), r, 50)
    assert given(t, TWO_T) and not given(t, TWO_W)


def test_101_offers_listing_answers_differently_get_the_same_meaning():
    """101, and each offer gets its own answer ids: one (welcome first), two (turn_away first) and three, all open at
    once, are answered welcome, each with its own answer, and no answer id is given twice."""
    r = world(one=50, two=50, three=50)
    s = advance(armed(r), r, 50)
    welcomes = {ONE_W, TWO_W, THREE_W}
    turns = {ONE_T, TWO_T, THREE_T}
    assert all(given(s, a) for a in welcomes) and not any(given(s, a) for a in turns)


# ---- 102 first open -----------------------------------------------------------------------------------------------

def test_102_the_earliest_in_rules_order_is_answered_first_whatever_the_order_they_showed():
    """102: three shows before one (40, 45) and one is earlier in rules.offers; the rule set at 60 answers one first."""
    r = world(three=40, one=45)
    s = advance(started(r), r, 60)
    step = decide_logged(s, r, 60, SetOrders((ON,)))
    assert said(step.lines) == [(60, f"{ONE_W}.said"), (60, f"{THREE_W}.said")]


# ---- 103 never dead -----------------------------------------------------------------------------------------------

def test_103_the_order_is_on_before_and_after_every_offer_of_its_kind_is_answered():
    """103: order_states is ON for the true order before any offer shows, while one is open, and after every offer of
    the kind is answered; never PASSED_OVER."""
    r = world(one=50)
    for t in (10, 50, 10**5):
        assert view(advance(armed(r), r, t), r).order_states == (OrderState.ON,), t
    assert ON in advance(armed(r), r, 10**5).orders


def test_103_a_rule_whose_latch_is_false_is_waiting():
    """103: the same order on a latch that has not risen is WAITING, so ON above is the latch and not a constant."""
    r = world(one=50)
    s = started(r, SetOrders((Order(AfterTime(10**6), rule()),)))
    assert view(advance(s, r, 100), r).order_states == (OrderState.WAITING,)
    assert not answered(advance(s, r, 100), ONE)


def test_103_a_later_offer_is_answered_long_after_the_first():
    """103: one is answered at 50 and three shows at 10**5, answered at that instant by the same order."""
    r = world(one=50, three=10**5)
    s = advance(armed(r), r, 10**5)
    assert given(s, ONE_W) and given(s, THREE_W) and ON in s.orders


# ---- 104 refusals -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("t", [10, 60])
def test_104_the_player_may_not_send_it_with_or_without_an_open_offer(t: int):
    """104: decide of an AnswerKind raises InvalidVerbError whether an offer of the kind is open (t=60) or not (10), and
    nothing is written."""
    r = world(one=50)
    s = advance(new_save(r), r, t)
    with pytest.raises(InvalidVerbError):
        decide(s, r, t, rule())
    assert not answered(s, ONE)


def test_104_set_queue_refuses_an_entry_holding_it():
    """104: SetQueue with an entry holding the kind's answer raises InvalidVerbError, even with an offer open."""
    r = world(one=50)
    for t in (0, 60):
        with pytest.raises(InvalidVerbError):
            decide(advance(new_save(r), r, t), r, t, SetQueue((QueueEntry(rule(), NEVER),)))


def test_104_set_orders_accepts_a_declared_pair_with_no_offer_open():
    """104: a declared kind and role is accepted before any offer of the kind is shown and held in save.orders."""
    r = world(one=500)
    s = armed(r)
    assert s.orders == (ON,) and not shown(s, ONE)


@pytest.mark.parametrize("kind, role", [
    (KindId("nope"), WELCOME), (ARRIVAL, RoleId("maybe")), (STRANGER_KIND, RoleId("maybe")),
])
def test_104_set_orders_refuses_an_undeclared_kind_or_a_role_the_kind_lacks(kind: KindId, role: RoleId):
    """104: an undeclared kind, or a role the kind does not have (here also one that exists nowhere), raises
    InvalidVerbError."""
    r = world(one=50)
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), rule(kind, role)),)))


# ---- 105 validation -----------------------------------------------------------------------------------------------

def _answers(ids: tuple[str, ...], *roles: RoleId | None) -> tuple[AnswerDef, ...]:
    return tuple(answer_def(AnswerId(a), ro) for a, ro in zip(ids, roles))


@pytest.mark.parametrize("offers", [
    (OfferDef(ONE, _answers(("va", "vb"), WELCOME, TURN_AWAY)),),
    (OfferDef(ONE, _answers(("va", "vb"), WELCOME, None), kind=ARRIVAL),),
    (OfferDef(ONE, _answers(("va", "vb"), WELCOME, WELCOME), kind=ARRIVAL),),
    (kinded(ONE, ARRIVAL, ONE_W, ONE_T), OfferDef(TWO, _answers(("wa", "wb"), WELCOME, RoleId("other")), kind=ARRIVAL)),
], ids=["role on an unkinded offer", "no role on a kinded answer", "two answers one role", "role sets differ"])
def test_105_the_rules_are_invalid(offers: tuple[OfferDef, ...]):
    """105: InvalidRulesError for a role on an unkinded offer, a kinded offer's answer with no role, two answers of one
    offer with one role, and two offers of one kind with different role sets."""
    with pytest.raises(InvalidRulesError):
        town(show_at=None, offers=offers)


def test_105_the_valid_shapes_are_valid():
    """105, the controls: a kind with one offer, roles in a different order and different ids across the kind's
    offers, and an unkinded offer are all valid (so the refusals above are not a validator that refuses every kind)."""
    world(one=50)
    town(show_at=None, offers=(kinded(ONE, ARRIVAL, ONE_W, ONE_T),
                               OfferDef(TWO, (answer_def(TWO_T, TURN_AWAY), answer_def(TWO_W, WELCOME)), kind=ARRIVAL)))


# ---- 106 codec ----------------------------------------------------------------------------------------------------

def test_106_a_save_holding_the_rule_round_trips_before_and_after_it_answers():
    """106: decode(encode(s, r), r) == s for kinded rules, with the AnswerKind order in the save."""
    r = world(one=50)
    for t in (10, 100):
        s = advance(armed(r), r, t)
        assert decode(encode(s, r), r) == s
