"""Validation of day two's rules (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Validation",
"Installs land once", "Queued one-off", "Offers"; invariant 67; invariant 27 as amended). InvalidRulesError for: a
RuleInstall of a card off a ruled lane, Outcome.orders outside a trigger's or an answer's outcome, Outcome.queues
outside an answer's outcome or naming a card off HANDS or uncapped, an ANSWERED or ANSWER unlock in any Outcome.unlocks
or the opening, an offer with fewer than two answers, an answer id used twice across offers. Each refusal has an
accepted control beside it."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerDef, AnswerId, AtLeast, CardDef, CardId, InvalidRulesError, InvalidVerbError, OfferDef, OfferId,
    Order, Outcome, Rules, RuleInstall, SetOrders, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked,
    decide, new_save, validate_rules,
)
from town_world import ASK, H, HC, NO, R, T1, TC, YES, town

GO = TriggerId("go")
ANSWERS = (Unlock(UnlockKind.ANSWERED, ASK), Unlock(UnlockKind.ANSWER, YES))
"""The two kinds only an applied AnswerOffer adds (invariant 61)."""


def trigger(outcome: Outcome) -> tuple[TriggerDef, ...]:
    return (TriggerDef(GO, AfterTime(10), outcome),)


def capped(outcome: Outcome = Outcome(), finished: Outcome = Outcome()) -> tuple[CardDef, ...]:
    """A capped hands card carrying the outcome under test (a card's outcome and its finished)."""
    return (CardDef(CardId("c"), 100, cap=1, outcome=outcome, finished=finished),)


@pytest.mark.parametrize("card", [H, R, CardId("nope")])
def test_an_install_of_a_card_off_a_ruled_lane_is_invalid_and_a_ruled_one_is_valid(card: CardId):
    """A RuleInstall's card is a declared card on a ruled lane: the hands, the (unruled) rack or no card refuse; t1 and
    tc, locked when the install lands, are valid (an order may name a locked card)."""
    with pytest.raises(InvalidRulesError):
        town(yes=Outcome(orders=(RuleInstall(card),)))
    with pytest.raises(InvalidRulesError):
        town(triggers=trigger(Outcome(orders=(RuleInstall(card, first=True),))))
    town(yes=Outcome(orders=(RuleInstall(T1), RuleInstall(TC, first=True))))
    town(triggers=trigger(Outcome(orders=(RuleInstall(TC),))))


def test_installs_only_in_a_triggers_or_an_answers_outcome():
    """Outcome.orders is empty outside a trigger's and an answer's outcome: a card's outcome and its finished refuse."""
    install = Outcome(orders=(RuleInstall(T1),))
    for cards in (capped(outcome=install), capped(finished=install)):
        with pytest.raises(InvalidRulesError):
            town(cards=cards)
    town(cards=capped())


def test_queues_only_in_an_answers_outcome():
    """Outcome.queues is empty outside an answer's outcome: a trigger's, a card's outcome and its finished refuse."""
    queue = Outcome(queues=(HC,))
    with pytest.raises(InvalidRulesError):
        town(triggers=trigger(queue))
    for cards in (capped(outcome=queue), capped(finished=queue)):
        with pytest.raises(InvalidRulesError):
            town(cards=cards)
    town(no=queue)


@pytest.mark.parametrize("card", [H, TC, R, CardId("nope")])
def test_a_queued_card_is_a_declared_capped_hands_card(card: CardId):
    """Each queued card is a declared HANDS card with a cap: h (uncapped), tc (capped, on the town), r (the rack) and
    an unknown card refuse; hc is valid."""
    with pytest.raises(InvalidRulesError):
        town(no=Outcome(queues=(card,)))
    town(no=Outcome(queues=(HC,)))


@pytest.mark.parametrize("u", ANSWERS)
def test_no_outcome_and_no_opening_holds_an_answered_or_answer_unlock(u: Unlock):
    """Invariant 67: only an applied AnswerOffer adds ANSWERED and ANSWER, so no Outcome.unlocks (a card's, a trigger's,
    an answer's) and no opening holds one; an OFFER unlock is valid in all of them (the control)."""
    builds: tuple[Callable[[], Rules], ...] = (
        lambda: town(cards=capped(outcome=Outcome(unlocks=(u,)))),
        lambda: town(triggers=trigger(Outcome(unlocks=(u,)))),
        lambda: town(yes=Outcome(unlocks=(u,))))
    for build in builds:
        with pytest.raises(InvalidRulesError):
            build()
    r = town()
    assert r.opening is not None
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(r, opening=r.opening + (u,)))
    show = Unlock(UnlockKind.OFFER, ASK)
    town(cards=capped(outcome=Outcome(unlocks=(show,))), triggers=trigger(Outcome(unlocks=(show,))))
    validate_rules(replace(r, opening=r.opening + (show,)))


def with_offers(*offers: OfferDef) -> Rules:
    return replace(town(), offers=offers)


def test_an_offer_needs_two_answers_and_answer_ids_are_unique_across_offers():
    """Offers: at least two answers; answer ids unique across all offers; offer ids unique."""
    one = OfferDef(OfferId("one"), (AnswerDef(AnswerId("only"), Outcome()),))
    clash = OfferDef(OfferId("two"), (AnswerDef(YES, Outcome()), AnswerDef(AnswerId("other"), Outcome())))
    again = OfferDef(ASK, (AnswerDef(AnswerId("a1"), Outcome()), AnswerDef(AnswerId("a2"), Outcome())))
    for bad in (with_offers(*town().offers, one), with_offers(*town().offers, clash), with_offers(*town().offers, again)):
        with pytest.raises(InvalidRulesError):
            validate_rules(bad)
    fine = OfferDef(OfferId("two"), (AnswerDef(AnswerId("b1"), Outcome()), AnswerDef(AnswerId("b2"), Outcome())))
    validate_rules(with_offers(*town().offers, fine))


@pytest.mark.parametrize("u", [Unlock(UnlockKind.OFFER, ASK), *ANSWERS, Unlock(UnlockKind.ANSWER, NO)])
def test_unlocked_conditions_on_the_three_new_kinds_name_declared_ids(u: Unlock):
    """The three new UnlockKinds are unlock categories gates read as any unlock (CONTRACT: OFFERS): an Unlocked
    condition on a declared offer or answer is accepted by SetOrders and a trigger's requires; on an undeclared id it
    is refused."""
    r = town(triggers=(TriggerDef(GO, AfterTime(10), Outcome(), (AtLeast(Unlocked(u), 1, 1),)),))
    s = decide(new_save(r), r, 0, SetOrders((Order(AtLeast(Unlocked(u), 1, 1), TapCard(T1)),)))
    assert len(s.orders) == 1
    unknown = Unlock(u.kind, "nope")
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, SetOrders((Order(AtLeast(Unlocked(unknown), 1, 1), TapCard(T1)),)))
    with pytest.raises(InvalidRulesError):
        town(triggers=(TriggerDef(GO, AfterTime(10), Outcome(), (AtLeast(Unlocked(unknown), 1, 1),)),))
