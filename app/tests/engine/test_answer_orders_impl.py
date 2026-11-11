"""Answering an offer as an order or a queue entry (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS",
"Evaluation applies every verb", "Dead", "Evaluation after a cascade", invariants 57, 61 and 62): an answer order acts
at the first instant it can, before tap orders; one that cannot act changes nothing; an answered offer's order is
passed over and its queue entry settles."""
import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AnswerDef, AnswerId, AnswerOffer, AtLeast, CardCount, CardDef, CardId,
    InvalidVerbError, LaneDef, LaneId, LineKey, OfferDef, OfferId, Order, OrderState, Outcome, PacingCurve, QueueEntry,
    RuleInstall, Rules, Save, SetOrders, SetQueue, SkillDef, SkillId, StoreDef, StoreId, TapCard, TriggerDef, TriggerId,
    Unlock, UnlockKind, advance, advance_logged, decide, decide_logged, new_save, validate_rules, view,
)

HELPER = LaneId("helper")
H, A, B = CardId("h"), CardId("a"), CardId("b")
O = OfferId("o")
YES, NO = AnswerId("yes"), AnswerId("no")
ALWAYS = AfterTime(0)
ANSWER_YES = Order(ALWAYS, AnswerOffer(O, YES))


def world(at: int = 50, max_firings: int = 1000) -> Rules:
    show = TriggerDef(TriggerId("offer_o"), AfterTime(at), Outcome(unlocks=(Unlock(UnlockKind.OFFER, O),)))
    yes = Outcome(unlocks=(Unlock(UnlockKind.CARD, B),), orders=(RuleInstall(B, first=True),), lines=(LineKey("l_yes"),))
    r = Rules(stores=(StoreDef(StoreId("x"), 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(HELPER, True),),
              cards=(CardDef(H, 10), CardDef(A, 10, lane=HELPER), CardDef(B, 30, lane=HELPER, cap=1)),
              triggers=(show,), offers=(OfferDef(O, (AnswerDef(YES, yes), AnswerDef(NO))),),
              opening=(Unlock(UnlockKind.CARD, H), Unlock(UnlockKind.CARD, A)), max_firings_per_instant=max_firings)
    validate_rules(r)
    return r


def planned(r: Rules, *orders: Order) -> Save:
    return decide(new_save(r), r, 0, SetOrders(orders))


def test_an_answer_order_waits_for_its_offer_then_acts_at_the_instant_it_shows():
    r = world()
    s = planned(r, ANSWER_YES, Order(ALWAYS, TapCard(A)))
    assert view(s, r).order_states[0] is OrderState.ON and Unlock(UnlockKind.ANSWERED, O) not in s.unlocked
    step = advance_logged(s, r, 50)
    assert Unlock(UnlockKind.ANSWER, YES) in step.save.unlocked
    assert [ln.key for ln in step.lines if ln.time == 50] == ["l_yes"]
    assert step.save.orders[0] == Order(ALWAYS, TapCard(B))
    assert view(step.save, r).order_states[1] is OrderState.PASSED_OVER


def test_an_answer_by_order_and_by_the_player_land_the_same():
    """Invariant 62: equal stores, cards, lanes, unlocked, modifiers and fired, orders differing by the answer order,
    and equal lines at the instant."""
    r = world()
    by_order = advance_logged(planned(r, ANSWER_YES), r, 50)
    by_player = decide_logged(planned(r), r, 50, AnswerOffer(O, YES))
    a, b = by_order.save, by_player.save
    for part in ("stores", "cards", "lanes", "unlocked", "modifiers", "fired"):
        assert getattr(a, part) == getattr(b, part), part
    assert tuple(o for o in a.orders if o != ANSWER_YES) == b.orders
    assert [ln.key for ln in by_order.lines] == [ln.key for ln in by_player.lines]


def test_answer_orders_come_before_tap_orders_and_the_second_answer_changes_nothing():
    r = world(at=0)
    s = planned(r, Order(ALWAYS, TapCard(A)), Order(ALWAYS, AnswerOffer(O, NO)), ANSWER_YES)
    assert Unlock(UnlockKind.ANSWER, NO) in s.unlocked and Unlock(UnlockKind.ANSWER, YES) not in s.unlocked
    assert s.lanes[1].card == A
    assert view(s, r).order_states == (OrderState.ON, OrderState.PASSED_OVER, OrderState.PASSED_OVER)


def test_a_queued_answer_answers_when_it_controls_and_settles():
    r = world()
    s = decide(new_save(r), r, 0, SetQueue((QueueEntry(AnswerOffer(O, NO), AfterTime(10**9)),
                                            QueueEntry(TapCard(H), AtLeast(CardCount(H), 1, 1)))))
    assert s.queue[0].verb == AnswerOffer(O, NO) and s.lanes[0].card is None   # the head waits for its offer
    later = advance(s, r, 50)
    assert Unlock(UnlockKind.ANSWER, NO) in later.unlocked
    assert later.queue == (QueueEntry(TapCard(H), AtLeast(CardCount(H), 1, 1)),) and later.lanes[0].card == H


def test_a_queued_answer_of_an_offer_the_player_answered_settles_at_once():
    r = world(at=0)
    s = decide(new_save(r), r, 0, SetQueue((QueueEntry(AnswerOffer(O, NO), AfterTime(10**9)),)))
    assert s.queue == ()   # it answered at once, and settled
    s = decide(new_save(r), r, 0, AnswerOffer(O, YES))
    s = decide(s, r, 0, SetQueue((QueueEntry(AnswerOffer(O, NO), AfterTime(10**9)),)))
    assert s.queue == () and Unlock(UnlockKind.ANSWER, NO) not in s.unlocked


def test_set_orders_refuses_an_answer_not_of_its_offer_and_accepts_one_not_shown_yet():
    r = world()
    with pytest.raises(InvalidVerbError):
        planned(r, Order(ALWAYS, AnswerOffer(O, AnswerId("maybe"))))
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, SetQueue((QueueEntry(AnswerOffer(OfferId("p"), YES), ALWAYS),)))
    assert planned(r, ANSWER_YES).orders == (ANSWER_YES,)


def test_an_answer_left_by_a_cascade_acts_one_second_on():
    """Two firings an instant: at 50 the player's tap of h lands and the trigger shows the offer, so the answer waits;
    the one READY at 51 (the verbs with no card) answers it."""
    r = world(max_firings=2)
    s = decide(planned(r, ANSWER_YES), r, 40, TapCard(H))
    at = advance(s, r, 50)
    assert at.last_cascade is not None and at.last_cascade.time == 50
    assert Unlock(UnlockKind.ANSWERED, O) not in at.unlocked
    assert Unlock(UnlockKind.ANSWERED, O) in advance(at, r, 51).unlocked
