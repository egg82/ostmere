"""Offers and AnswerOffer (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Offers", "ANSWERED and
ANSWER are written ... whatever rules.opening is", "AnswerOffer", "Dead", "No new event", "Covered"; invariants 61 and
62; api CONTRACT.txt, "OFFERS"). An offer is shown once Unlock(OFFER) is held, open until answered, and never expires.
An applied AnswerOffer adds Unlock(ANSWERED, o) and Unlock(ANSWER, a), lands the answer's outcome as a trigger's (lines
with card None), then orders and the queue evaluate. The player's bad answer raises; an order's or the queue's changes
nothing. Evaluation picks a true order's answer that can act before any tap."""
import pytest

from ashfall_app.engine import (
    HANDS, AfterTime, AnswerId, AnswerOffer, AtLeast, DecisionContext, InvalidVerbError, OfferId,
    Order, OrderState, Outcome, QueueEntry, SetOrders, SetQueue, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, advance,
    advance_logged, decide, decide_logged, new_save, view,
)
from cards_world import keys, ledger
from town_world import (
    ASK, H, LATER, M, NEVER, NO, OTHER, SECOND, SHOW_AT, T1, T2, TC, TOWN, X, YES, answer, answered, given, running, shown, started, town,
)


def by_order(a: AnswerId, when: AfterTime | AtLeast = AfterTime(0), offer: OfferId = ASK) -> Order:
    return Order(when, AnswerOffer(offer, a))


# ---- shown, open, answered -------------------------------------------------------------------------------------

def test_an_offer_shows_when_its_unlock_lands_and_stays_open_for_good():
    """An offer is shown once Unlock(OFFER, o) is in the unlock set and open while not answered; nothing in the engine
    closes it (invariant 61: an open offer stays open across every advance in which nothing answers it)."""
    r = town()
    s = advance(new_save(r), r, SHOW_AT - 1)
    assert not shown(s, ASK)
    s = advance(s, r, SHOW_AT)
    assert shown(s, ASK) and not answered(s, ASK)
    for t in (SHOW_AT + 1, 10**5, 10**8):
        s = advance(s, r, t)
        assert shown(s, ASK) and not answered(s, ASK) and not given(s, YES) and not given(s, NO), t


def test_the_players_answer_adds_both_unlocks_lands_the_outcome_and_evaluates():
    """AnswerOffer: Unlock(ANSWERED, ask) and Unlock(ANSWER, yes) enter together; the outcome lands (tc unlocked, its
    always rule installed at the top) and orders evaluate at once, so tc starts at the answer's instant; the answer's
    lines are in the Step with card None (CONTRACT: "The answer's lines are in Step.lines at once")."""
    r = town()
    s = advance(new_save(r), r, 60)
    step = decide_logged(s, r, 60, AnswerOffer(ASK, YES))
    a = step.save
    assert answered(a, ASK) and given(a, YES) and not given(a, NO)
    assert a.orders[0] == Order(AfterTime(0), TapCard(TC)) and running(a, TOWN) == TC
    said = [ln for ln in step.lines if ln.key == "yes.said"]
    assert len(said) == 1 and said[0].time == 60 and said[0].card is None


@pytest.mark.parametrize("verb, at", [
    (AnswerOffer(OfferId("nope"), YES), 60),
    (AnswerOffer(ASK, LATER), 60),
    (AnswerOffer(ASK, AnswerId("maybe")), 60),
    (AnswerOffer(ASK, YES), SHOW_AT - 1),
    (AnswerOffer(OTHER, LATER), 60),
])
def test_a_players_bad_answer_raises(verb: AnswerOffer, at: int):
    """From the player: an unknown offer, an answer not of that offer (another offer's, or none's), an offer not shown
    (before 50; the second offer is never shown) raises InvalidVerbError (CONTRACT: 422, nothing written)."""
    r = town(offers=(SECOND,))
    s = advance(new_save(r), r, at)
    with pytest.raises(InvalidVerbError):
        decide(s, r, at, verb)


def test_answering_an_answered_offer_raises_with_either_answer():
    """Invariant 61: "a player's AnswerOffer of ... an answered one raises InvalidVerbError", whichever answer."""
    r = town()
    s = answer(advance(new_save(r), r, 60), r, 60, YES)
    for a in (YES, NO):
        with pytest.raises(InvalidVerbError):
            decide(s, r, 70, AnswerOffer(ASK, a))


# ---- answered by an order, while away ------------------------------------------------------------------------

def test_an_order_answers_at_the_instant_the_offer_shows_with_its_lines_in_that_instant():
    """"No new event" and "Answered while away": a true answer order acts at the instant its offer shows; its lines
    follow the showing trigger's at that instant, card None; the player's answer afterwards raises (CONTRACT: a rule
    may have answered it since the page's last view)."""
    r = town()
    s = started(r, SetOrders((by_order(NO),)))
    assert not answered(s, ASK)
    step = advance_logged(s, r, 1000)
    assert keys([ln for ln in step.lines if ln.time == SHOW_AT])[:2] == [(SHOW_AT, "ask.shown"), (SHOW_AT, "no.said")]
    assert all(ln.card is None for ln in step.lines if ln.key in ("ask.shown", "no.said"))
    assert given(advance(s, r, SHOW_AT), NO) and not given(advance(s, r, SHOW_AT - 1), NO)
    with pytest.raises(InvalidVerbError):
        decide(step.save, r, 1000, AnswerOffer(ASK, YES))


def test_an_order_whose_latch_rises_later_answers_at_that_latch():
    """"one whose latch rises later acts at that LATCH": AfterTime(80) answers at 80, not before."""
    r = town()
    s = started(r, SetOrders((by_order(YES, AfterTime(80)),)))
    assert not answered(advance(s, r, 79), ASK)
    assert given(advance(s, r, 80), YES)


def test_an_answer_order_waits_on_while_its_offer_is_not_shown_and_is_passed_over_once_answered():
    """Dead: an AnswerOffer of an offer not yet shown is not dead (ON while its latch is true); of an answered offer,
    by anyone, it is dead, so its order is PASSED_OVER; an order answering an answered offer changes nothing. (The yes
    answer here installs nothing, so the list stays these two.)"""
    r = town(yes=Outcome())
    s = started(r, SetOrders((by_order(NO, AfterTime(10**6)), by_order(YES))))
    assert view(s, r).order_states == (OrderState.WAITING, OrderState.ON)
    s = advance(s, r, 10**6)
    assert given(s, YES) and not given(s, NO)
    assert view(s, r).order_states == (OrderState.PASSED_OVER, OrderState.PASSED_OVER)


def test_set_orders_and_set_queue_refuse_an_undeclared_pair_and_accept_an_offer_not_yet_shown():
    """SetOrders and SetQueue refuse an AnswerOffer whose pair is not a declared offer and one of its answers (CONTRACT:
    422); a pair whose offer is not shown yet is accepted (planning ahead)."""
    r = town(offers=(SECOND,))
    s = new_save(r)
    for bad in (AnswerOffer(ASK, LATER), AnswerOffer(OfferId("nope"), YES), AnswerOffer(ASK, AnswerId("maybe"))):
        with pytest.raises(InvalidVerbError):
            decide(s, r, 0, SetOrders((Order(AfterTime(0), bad),)))
        with pytest.raises(InvalidVerbError):
            decide(s, r, 0, SetQueue((QueueEntry(bad, NEVER),)))
    assert decide(s, r, 0, SetOrders((by_order(LATER, offer=OTHER),))).orders == (by_order(LATER, offer=OTHER),)
    assert len(decide(s, r, 0, SetQueue((QueueEntry(AnswerOffer(ASK, YES), NEVER),))).queue) == 1


# ---- the queue ---------------------------------------------------------------------------------------------------

def test_a_queue_head_answer_waits_for_its_offer_then_answers_and_pops_whatever_its_until():
    """The queue's head waits while its offer is not shown, holding the entries behind it; it answers once shown and,
    dead for good, pops at that instant though its `until` never holds (CONTRACT: "it is gone once the offer is
    answered"); the next entry then controls and taps h."""
    r = town()
    s = started(r, SetQueue((QueueEntry(AnswerOffer(ASK, YES), NEVER), QueueEntry(TapCard(H), NEVER))))
    assert len(s.queue) == 2 and running(s, HANDS) is None
    s = advance(s, r, SHOW_AT)
    assert given(s, YES)
    assert s.queue == (QueueEntry(TapCard(H), NEVER),) and running(s, HANDS) == H


def test_a_queued_answer_behind_the_head_pops_at_the_instant_its_offer_is_answered():
    """Dead: a queue entry holding an AnswerOffer of an answered offer settles and pops at that instant, whatever its
    `until`, wherever it stands; here behind a head that never pops, answered by the player."""
    r = town()
    head = QueueEntry(TapCard(H), NEVER)
    s = started(r, SetQueue((head, QueueEntry(AnswerOffer(ASK, NO), NEVER))))
    s = answer(advance(s, r, 60), r, 60, YES)
    assert s.queue == (head,) and not given(s, NO)


# ---- both ways, order of evaluation, opening None --------------------------------------------------------------

@pytest.mark.parametrize("a", [YES, NO])
def test_answering_by_hand_and_by_order_land_alike(a: AnswerId):
    """Invariant 62: decide(s, r, T, AnswerOffer(o, a)) and the save in which "AfterTime(0) -> AnswerOffer(o, a)" acted
    at T have equal stores, cards, lanes, unlocked, modifiers and fired; their orders differ only by that order; their
    lines at T are equal in order."""
    r = town()
    s = advance(started(r, SetOrders((Order(NEVER, TapCard(H)),))), r, 60)
    by_hand = decide_logged(s, r, 60, AnswerOffer(ASK, a))
    order = decide_logged(s, r, 60, SetOrders(s.orders + (by_order(a),)))
    x, y = by_hand.save, order.save
    assert (x.stores, x.cards, x.lanes, x.unlocked, x.modifiers, x.fired) == \
        (y.stores, y.cards, y.lanes, y.unlocked, y.modifiers, y.fired)
    assert [o for o in y.orders if o != by_order(a)] == list(x.orders)
    assert keys([ln for ln in by_hand.lines if ln.time == 60]) == keys([ln for ln in order.lines if ln.time == 60])


def test_a_true_answer_order_acts_before_a_tap_order_at_one_instant():
    """The controlling verb: the AnswerOffer of the first true order that can act comes before any TapCard, so an
    answer starting t2 takes the town before a tap order on t1 (on from the same instant) can; without the answer
    order, t1 takes it (the control)."""
    r = town(yes=Outcome(starts=(T2,)))
    tap_rule = Order(AtLeast(Unlocked(Unlock(UnlockKind.OFFER, ASK)), 1, 1), TapCard(T1))
    s = advance(started(r, SetOrders((tap_rule, by_order(YES)))), r, SHOW_AT)
    assert given(s, YES) and running(s, TOWN) == T2
    s = advance(started(r, SetOrders((tap_rule,))), r, SHOW_AT)
    assert running(s, TOWN) == T1


def test_with_no_opening_answers_are_written_and_counted_only_once_given():
    """ANSWERED and ANSWER are written to save.unlocked whatever rules.opening is, and counted only when present: with
    opening None every offer is shown from time 0 (View.unlocked holds it), an Unlocked(ANSWERED) rule waits until the
    answer, and View.unlocked holds the two only once save.unlocked does."""
    r = town(gated=False)
    s = new_save(r)
    gate = Order(AtLeast(Unlocked(Unlock(UnlockKind.ANSWERED, ASK)), 1, 1), TapCard(T1))
    s = decide(s, r, 0, SetOrders((gate,)))
    assert Unlock(UnlockKind.OFFER, ASK) in view(s, r).unlocked
    assert Unlock(UnlockKind.ANSWERED, ASK) not in view(s, r).unlocked and running(s, TOWN) is None
    s = answer(s, r, 10, NO)
    assert set(s.unlocked) >= {Unlock(UnlockKind.ANSWERED, ASK), Unlock(UnlockKind.ANSWER, NO)}
    assert Unlock(UnlockKind.ANSWER, YES) not in s.unlocked and Unlock(UnlockKind.ANSWER, YES) not in view(s, r).unlocked
    assert {Unlock(UnlockKind.ANSWERED, ASK), Unlock(UnlockKind.ANSWER, NO)} <= set(view(s, r).unlocked)
    assert running(s, TOWN) == T1


def test_the_decision_context_records_an_answer_with_no_card():
    """Decision context records AnswerOffer like any verb, with no card (in_mix False)."""
    r = town()
    step = decide_logged(advance(new_save(r), r, 60), r, 60, AnswerOffer(ASK, YES))
    assert step.context == DecisionContext(None, False, ())


def test_an_answer_order_covers_no_store():
    """Covered: an AnswerOffer covers no store, even one whose answer starts a card making it; a TapCard order of that
    card does (the control)."""
    r = town(no=Outcome(starts=(M,)))
    s = started(r, SetOrders((by_order(NO, NEVER),)))
    assert not ledger(s, r, X).covered
    assert ledger(started(r, SetOrders((Order(NEVER, TapCard(M)),))), r, X).covered



def test_after_the_firing_cap_an_answer_waiting_to_act_gets_a_ready_at_the_next_second():
    """Evaluation after a cascade: when the cap suspended evaluation at T, a READY falls at T + 1 whenever a true
    order's AnswerOffer, or the controlling queue entry's, could act. With a cap of two firings, the showing trigger
    and a second trigger spend it at 50; the answer acts at 51 (its READY one firing, the answer the other), by an
    order and by the queue alike."""
    r = town(max_firings=2, triggers=(TriggerDef(TriggerId("also"), AfterTime(SHOW_AT), Outcome()),))
    for plan in (SetOrders((by_order(NO),)), SetQueue((QueueEntry(AnswerOffer(ASK, NO), NEVER),))):
        s = advance(started(r, plan), r, SHOW_AT)
        assert shown(s, ASK) and not answered(s, ASK)
        assert s.last_cascade is not None and s.last_cascade.time == SHOW_AT
        assert given(advance(s, r, SHOW_AT + 1), NO)
