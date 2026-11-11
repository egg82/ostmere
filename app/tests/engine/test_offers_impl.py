"""Offers answered by the player (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS", "Offers",
"AnswerOffer", "Queued one-off", "Read model", invariants 61, 64, 66 and 67): a trigger shows the offer, an answer
closes it with its two unlocks, lands its outcome and evaluates at once, and the view lists it."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    HANDS, QUANTITY_SCALE as Q, AfterTime, AnswerDef, AnswerId, AnswerOffer, AtLeast, CardCount, CardDef, CardId,
    InvalidRulesError, InvalidVerbError, LaneDef, LaneId, LineKey, OfferDef, OfferId, Order, Outcome, PacingCurve,
    QueueEntry, RuleInstall, Rules, SetQueue, SkillDef, SkillId, StoreDef, StoreId, TapCard, TriggerDef, TriggerId,
    Unlock, UnlockKind, Unlocked, IdKind, RebaseError, Rename, advance, decide, decide_logged, encode, new_save, rebase,
    validate_rules, view,
)

X = StoreId("x")
HELPER = LaneId("helper")
H, ONE, A, B = CardId("h"), CardId("one"), CardId("a"), CardId("b")
O = OfferId("o")
YES, NO = AnswerId("yes"), AnswerId("no")
SHOWN, ANSWERED = Unlock(UnlockKind.OFFER, O), Unlock(UnlockKind.ANSWERED, O)


def world(yes: Outcome = Outcome(), no: Outcome = Outcome(), gated: bool = True, at: int = 5) -> Rules:
    opening = (Unlock(UnlockKind.CARD, H), Unlock(UnlockKind.CARD, ONE), Unlock(UnlockKind.CARD, A))
    show = TriggerDef(TriggerId("offer_o"), AfterTime(at), Outcome(unlocks=(SHOWN,), lines=(LineKey("l_asked"),)))
    after = TriggerDef(TriggerId("t_after"), AtLeast(Unlocked(ANSWERED), 1, 1), Outcome(lines=(LineKey("l_after"),)))
    r = Rules(stores=(StoreDef(X, 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(HELPER, True),),
              cards=(CardDef(H, 10), CardDef(ONE, 20, cap=1), CardDef(A, 10, lane=HELPER), CardDef(B, 30, lane=HELPER)),
              triggers=(show, after), opening=opening if gated else None,
              offers=(OfferDef(O, (AnswerDef(YES, yes), AnswerDef(NO, no))),))
    validate_rules(r)
    return r


def test_an_offer_shows_by_its_trigger_and_stays_open():
    r = world()
    assert view(advance(new_save(r), r, 4), r).offers == ()
    v = view(advance(new_save(r), r, 10_000), r)
    assert [(o.offer, o.answer) for o in v.offers] == [(O, None)]


def test_the_answer_adds_both_unlocks_lands_its_outcome_and_the_gate_reads_it():
    """Invariant 61, and a trigger on "answered, either answer" fires at the answer's instant."""
    r = world(yes=Outcome(lines=(LineKey("l_yes"),)))
    step = decide_logged(advance(new_save(r), r, 10), r, 10, AnswerOffer(O, YES))
    assert ANSWERED in step.save.unlocked and Unlock(UnlockKind.ANSWER, YES) in step.save.unlocked
    assert Unlock(UnlockKind.ANSWER, NO) not in step.save.unlocked
    assert [(ln.key, ln.card) for ln in step.lines if ln.time == 10] == [("l_yes", None), ("l_after", None)]
    assert view(step.save, r).offers[0].answer == YES


@pytest.mark.parametrize("verb, at", [
    (AnswerOffer(OfferId("nope"), YES), 10), (AnswerOffer(O, AnswerId("maybe")), 10), (AnswerOffer(O, YES), 3),
])
def test_a_player_answer_that_cannot_act_is_refused(verb: AnswerOffer, at: int):
    r = world()
    with pytest.raises(InvalidVerbError):
        decide(advance(new_save(r), r, at), r, at, verb)


def test_an_answered_offer_refuses_a_second_answer():
    r = world()
    s = decide(advance(new_save(r), r, 10), r, 10, AnswerOffer(O, YES))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 10, AnswerOffer(O, NO))


def test_with_no_opening_every_offer_is_shown_and_only_the_given_answer_is_held():
    r = world(gated=False)
    s = new_save(r)
    assert [o.answer for o in view(s, r).offers] == [None]
    assert ANSWERED not in view(s, r).unlocked and SHOWN in view(s, r).unlocked
    s = decide(s, r, 0, AnswerOffer(O, NO))
    assert ANSWERED in s.unlocked and ANSWERED in view(s, r).unlocked and s.fired[1]


def test_an_answers_install_acts_at_once_above_the_lanes_default():
    """The first=True install goes above the lane's always rule, and acts at the answer's instant."""
    r = world(yes=Outcome(unlocks=(Unlock(UnlockKind.CARD, B),), orders=(RuleInstall(B, first=True),)))
    s = decide(advance(new_save(r), r, 10), r, 10, AnswerOffer(O, YES))
    assert s.orders == (Order(AfterTime(0), TapCard(B)),) and s.lanes[1].card == B


def test_a_queued_one_off_goes_first_and_starts_when_the_hands_are_free():
    """Invariant 66: at the front of the queue, as the page's When ready entry; started at once when the hands are
    free, else at the hands' landing; gone once the card completes."""
    r = world(yes=Outcome(queues=(ONE,)))
    plan = QueueEntry(TapCard(H), AtLeast(CardCount(H), 9, 9))
    s = decide(advance(new_save(r), r, 10), r, 10, SetQueue((plan,)))
    assert s.lanes[0].card == H
    s = decide(advance(s, r, 12), r, 12, AnswerOffer(O, YES))
    assert s.queue == (QueueEntry(TapCard(ONE), AtLeast(CardCount(ONE), 1, 1)), plan) and s.lanes[0].card == H
    landed = advance(s, r, 20)
    assert landed.lanes[0].card == ONE
    assert advance(landed, r, 40).queue == (plan,) and advance(landed, r, 40).lanes[0].card == H


def test_each_answer_names_its_card_and_what_a_tap_of_it_takes_now():
    """Invariant 64."""
    r = world(yes=Outcome(queues=(ONE,)), no=Outcome(orders=(RuleInstall(B, first=True),)))
    v = view(advance(new_save(r), r, 10), r)
    assert [(a.answer, a.card, a.takes_s) for a in v.offers[0].answers] == [(YES, ONE, 20), (NO, B, 30)]


BAD: list[Callable[[Rules], Rules]] = [
    lambda r: replace(r, offers=(OfferDef(O, (AnswerDef(YES),)),)),
    lambda r: replace(r, offers=(*r.offers, OfferDef(OfferId("p"), (AnswerDef(YES), AnswerDef(AnswerId("z")))))),
    lambda r: replace(r, opening=(*(r.opening or ()), ANSWERED)),
    lambda r: replace(r, triggers=(TriggerDef(TriggerId("t"), AfterTime(0), Outcome(unlocks=(ANSWERED,))),)),
    lambda r: replace(r, offers=(OfferDef(O, (AnswerDef(YES, Outcome(queues=(A,))), AnswerDef(NO))),)),
    lambda r: replace(r, offers=(OfferDef(O, (AnswerDef(YES, Outcome(queues=(H,))), AnswerDef(NO))),)),
    lambda r: replace(r, offers=(OfferDef(O, (AnswerDef(YES, Outcome(orders=(RuleInstall(H),))), AnswerDef(NO))),)),
]


@pytest.mark.parametrize("bad", BAD)
def test_invalid_offers_are_refused(bad: Callable[[Rules], Rules]):
    """Invariant 67, and the offer's own shape: two answers or more, answer ids unique across offers."""
    with pytest.raises(InvalidRulesError):
        validate_rules(bad(world()))


def test_the_hands_lane_is_not_ruled_by_an_offer():
    assert HANDS not in {d.id for d in world().lanes}


def test_a_rebase_renames_an_offer_and_its_answers_and_keeps_the_answer_given():
    r = world()
    s = decide(advance(new_save(r), r, 10), r, 10, AnswerOffer(O, YES))
    p, sure = OfferId("p"), AnswerId("sure")
    show = replace(r.triggers[0], outcome=Outcome(unlocks=(Unlock(UnlockKind.OFFER, p),), lines=(LineKey("l_asked"),)))
    after = replace(r.triggers[1], when=AtLeast(Unlocked(Unlock(UnlockKind.ANSWERED, p)), 1, 1))
    new = replace(r, triggers=(show, after), offers=(OfferDef(p, (AnswerDef(sure), AnswerDef(NO))),))
    renames = (Rename(IdKind.OFFER, O, p), Rename(IdKind.ANSWER, YES, sure))
    got = rebase(encode(s, r), new, renames)
    assert Unlock(UnlockKind.ANSWERED, p) in got.unlocked and Unlock(UnlockKind.ANSWER, sure) in got.unlocked
    assert view(got, new).offers[0].answer == sure


def test_a_rebase_that_moves_an_answer_to_another_offer_raises():
    r = world()
    s = advance(new_save(r), r, 10)
    moved = replace(r, offers=(OfferDef(O, (AnswerDef(AnswerId("a1")), AnswerDef(NO))),
                               OfferDef(OfferId("p"), (AnswerDef(YES), AnswerDef(AnswerId("a2"))))))
    with pytest.raises(RebaseError) as e:
        rebase(encode(s, r), moved)
    assert (e.value.kind, e.value.id) == (IdKind.ANSWER, YES)
