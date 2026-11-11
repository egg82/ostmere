"""A trigger whose `requires` names an unlock (engine DESIGN.txt, "Triggers"): it waits while the unlock is missing,
however long its `when` has held, and fires at the instant the unlock lands, whether a trigger's outcome or an answer
adds it."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AnswerDef, AnswerId, AnswerOffer, AtLeast, AtMost, CardDef, CardId, LineKey,
    OfferDef, OfferId, Outcome, PacingCurve, Rules, SkillDef, SkillId, StoreDef, StoreId, StoreValue, TriggerDef,
    TriggerId, Unlock, UnlockKind, Unlocked, advance, advance_logged, decide_logged, new_save, validate_rules,
)

X = StoreId("x")
H = CardId("h")
F = Unlock(UnlockKind.FEATURE, "f")
O = OfferId("o")
YES, NO = AnswerId("yes"), AnswerId("no")


def _has(u: Unlock) -> AtLeast:
    return AtLeast(Unlocked(u), 1, 1)


def world() -> Rules:
    """t_waits holds from 0 (x at most 0) and requires F, which t_open lands at 50; t_after holds from 0 and requires
    the offer answered."""
    triggers = (
        TriggerDef(TriggerId("t_waits"), AtMost(StoreValue(X), 0, 0), Outcome(lines=(LineKey("l_waits"),)),
                   requires=(_has(F),)),
        TriggerDef(TriggerId("t_open"), AfterTime(50), Outcome(unlocks=(F,), lines=(LineKey("l_open"),))),
        TriggerDef(TriggerId("offer_o"), AfterTime(5), Outcome(unlocks=(Unlock(UnlockKind.OFFER, O),))),
        TriggerDef(TriggerId("t_after"), AfterTime(0), Outcome(lines=(LineKey("l_after"),)),
                   requires=(_has(Unlock(UnlockKind.ANSWERED, O)),)),
    )
    r = Rules(stores=(StoreDef(X, 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), cards=(CardDef(H, 10),), triggers=triggers,
              opening=(Unlock(UnlockKind.CARD, H),),
              offers=(OfferDef(O, (AnswerDef(YES, Outcome()), AnswerDef(NO, Outcome()))),))
    validate_rules(r)
    return r


def test_a_trigger_waits_for_its_unlock_and_fires_the_instant_it_lands():
    r = world()
    early = advance(new_save(r), r, 49)
    assert early.fired == (False, False, True, False)
    step = advance_logged(early, r, 60)
    assert [(ln.time, ln.key) for ln in step.lines] == [(50, "l_open"), (50, "l_waits")]
    assert step.save.fired[:2] == (True, True)


def test_a_trigger_waiting_on_an_answer_fires_at_the_answer():
    r = world()
    s = advance(new_save(r), r, 40)
    assert not s.fired[3]
    step = decide_logged(s, r, 40, AnswerOffer(O, YES))
    assert step.save.fired[3] and (40, "l_after") in [(ln.time, ln.key) for ln in step.lines]
