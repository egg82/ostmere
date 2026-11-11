"""The read model of offers (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Read model", "The
answer's card"; invariant 64; api CONTRACT.txt, "OFFERS"). View.offers is every shown offer in rules order, each
OfferView(offer, answer, answers) with `answer` None while open; each AnswerView(answer, card, takes_s) in the offer's
answer order. An answer's card is the first card its outcome queues, else its first RuleInstall's, else the first card
it starts, else None; takes_s is one completion of that card started now from its current work at a full share
(tap_seconds' formula, for a locked card too), None without a card or at speed 0."""
import pytest

from ashfall_app.engine import (
    AfterTime, AnswerView, CardId, LaneSpeed, OfferView, Outcome, RuleInstall, TapCard, TriggerDef, TriggerId,
    Unlock, UnlockKind, WorkRef, advance, new_save, view,
)
from cards_world import mul
from town_world import ASK, HC, LATER, NO, OTHER, SECOND, SHOW_AT, SOONER, T1, T2, TC, TOWN, YES, answer, started, town


def test_no_offer_is_listed_before_it_shows_and_an_open_one_has_no_answer():
    """Invariant 64: exactly the shown offers; open, `answer` is None; answers in the offer's order, each with its
    card (yes installs tc: a locked card still has takes_s; no queues hc)."""
    r = town()
    assert view(advance(new_save(r), r, SHOW_AT - 1), r).offers == ()
    v = view(advance(new_save(r), r, SHOW_AT), r)
    assert v.offers == (OfferView(ASK, None, (AnswerView(YES, TC, 100), AnswerView(NO, HC, 100))),)


def test_offers_are_listed_in_rules_order_whatever_order_they_showed_in():
    """View.offers: every shown offer in rules order. The second offer shows at 20, the first at 50."""
    show_other = TriggerDef(TriggerId("show_other"), AfterTime(20), Outcome(unlocks=(Unlock(UnlockKind.OFFER, OTHER),)))
    r = town(offers=(SECOND,), triggers=(show_other,))
    assert [o.offer for o in view(advance(new_save(r), r, 30), r).offers] == [OTHER]
    assert [o.offer for o in view(advance(new_save(r), r, 60), r).offers] == [ASK, OTHER]
    other = view(advance(new_save(r), r, 30), r).offers[0]
    assert other == OfferView(OTHER, None, (AnswerView(LATER, None, None), AnswerView(SOONER, None, None)))


def test_an_answered_offer_stays_listed_with_its_answer():
    """`answer` is the a whose Unlock(ANSWER, a) is held."""
    r = town()
    v = view(answer(advance(new_save(r), r, 60), r, 60, NO), r)
    assert [(o.offer, o.answer) for o in v.offers] == [(ASK, NO)]


@pytest.mark.parametrize("outcome, card", [
    (Outcome(starts=(T2, T1), orders=(RuleInstall(TC), RuleInstall(T1)), queues=(HC,)), HC),
    (Outcome(starts=(T2,), orders=(RuleInstall(TC), RuleInstall(T1))), TC),
    (Outcome(starts=(T2, T1)), T2),
    (Outcome(), None),
])
def test_an_answers_card_is_its_first_queued_else_installed_else_started_card(outcome: Outcome, card: CardId | None):
    """The answer's card: first card its outcome queues, else the card of its first RuleInstall, else the first card it
    starts, else None (takes_s None then)."""
    r = town(yes=outcome)
    yes = view(advance(new_save(r), r, SHOW_AT), r).offers[0].answers[0]
    assert (yes.answer, yes.card) == (YES, card)
    assert (yes.takes_s is None) == (card is None)


def test_takes_s_reads_the_lanes_speed_the_cards_work_and_zero_speed():
    """takes_s: tap_seconds' formula. The town at half speed doubles tc's 100 s; hc tapped by hand at 0
    has 50 s of its completion left at 50; hc's work at 0% gives None."""
    r = town()
    s = advance(new_save(r, (mul(LaneSpeed(TOWN), 5000, "slow"),)), r, SHOW_AT)
    assert view(s, r).offers[0].answers[0] == AnswerView(YES, TC, 200)
    s = advance(started(r, TapCard(HC)), r, SHOW_AT)
    assert view(s, r).offers[0].answers[1] == AnswerView(NO, HC, 50)
    s = advance(new_save(r, (mul(WorkRef(HC), 0, "stuck"),)), r, SHOW_AT)
    assert view(s, r).offers[0].answers[1] == AnswerView(NO, HC, None)


def test_with_no_opening_every_offer_is_listed_from_time_0():
    """OFFER follows the usual rule: with opening None every offer is shown from time 0."""
    r = town(gated=False, show_at=None)
    assert [o.offer for o in view(new_save(r), r).offers] == [ASK]

