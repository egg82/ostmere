"""A dilemma offer's answers do what they say in the engine (opening/promise_checks.py): the promise's work is queued
when it is made; keeping it leaves that work queued, and breaking it retires the card, so the queue drops it."""
from dataclasses import replace

from ashfall_app.engine import (
    AnswerId, AnswerOffer, CardId, OfferId, Rules, Save, TapCard, Unlock, UnlockKind, decide, encode, new_save, rebase,
)
from ashfall_app.opening.promise_checks import promises
from ashfall_app.opening.schema import Opening, to_rules


def shown(s: Save, r: Rules, offer: str) -> Save:
    """`s` with `offer` shown, as its trigger would have."""
    return rebase(encode(replace(s, unlocked=(*s.unlocked, Unlock(UnlockKind.OFFER, offer))), r), r)


def queued(s: Save, card: str) -> bool:
    return any(isinstance(e.verb, TapCard) and e.verb.card == CardId(card) for e in s.queue)


def test_a_broken_promise_leaves_the_queue_and_a_kept_one_stays(shipped_opening: Opening):
    o, r = shipped_opening, to_rules(shipped_opening)
    dilemmas = [x for x in o.offers if x.tests]
    assert len(dilemmas) >= 3, "found almost no dilemmas: the check is blind"
    made = promises(o)
    for x in dilemmas:
        for p in x.tests:
            offer = next(y.id for y in o.offers for a in y.answers if a.id == p)
            s = decide(shown(new_save(r), r, offer), r, 0, AnswerOffer(OfferId(offer), AnswerId(p)))
            assert all(queued(s, c) for c in made[p]), f"{p} queued nothing: the control cannot fail"
            for a in x.answers:
                after = decide(shown(s, r, x.id), r, 0, AnswerOffer(OfferId(x.id), AnswerId(a.id)))
                for c in made[p]:
                    assert (Unlock(UnlockKind.RETIRED, c) in after.unlocked) == (p in a.breaks), a.id
                    assert queued(after, c) == (p not in a.breaks), a.id
