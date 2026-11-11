"""Where each offer stands, read off the unlock set: shown, answered, and by which answer. Reads only. Semantics:
DESIGN.txt, "Offers", "AnswerOffer", "The answer's card"."""
from .answers import AnswerKind, AnswerOffer
from .unlocked import is_unlocked
from .ids import AnswerId, CardId, OfferId
from .index import index
from .offers import AnswerDef
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind


def is_shown(save: Save, rules: Rules, offer: OfferId) -> bool:
    return is_unlocked(save, rules, Unlock(UnlockKind.OFFER, offer))


def is_answered(save: Save, rules: Rules, offer: OfferId) -> bool:
    """Answered, by either answer, from the instant Unlock(ANSWERED, offer) is held."""
    return is_unlocked(save, rules, Unlock(UnlockKind.ANSWERED, offer))


def answer_given(save: Save, rules: Rules, offer: OfferId) -> AnswerId | None:
    """The answer whose Unlock(ANSWER) is held, None while the offer is open or unknown."""
    found = index(rules).offers.get(offer)
    answers = () if found is None else found.answers
    return next((a.id for a in answers if is_unlocked(save, rules, Unlock(UnlockKind.ANSWER, a.id))), None)


def refusal(save: Save, rules: Rules, verb: AnswerOffer) -> str | None:
    """Why `verb` cannot act now (an unknown offer, an answer not of it, an offer not shown or already answered), or
    None when it can."""
    pair = index(rules).answers.get(verb.answer)
    if verb.offer not in index(rules).offers:
        return f"unknown offer {verb.offer}"
    if pair is None or pair[0] != verb.offer:
        return f"answer {verb.answer} is not one of offer {verb.offer}'s"
    if not is_shown(save, rules, verb.offer):
        return f"offer {verb.offer} is not shown"
    if is_answered(save, rules, verb.offer):
        return f"offer {verb.offer} is already answered"
    return None


def can_answer(save: Save, rules: Rules, verb: AnswerOffer) -> bool:
    return refusal(save, rules, verb) is None


def resolved(save: Save, rules: Rules, verb: AnswerKind) -> AnswerOffer | None:
    """The AnswerOffer `verb` applies now: the first open offer of its kind in rules order, answered with its answer of
    the role; None when no offer of the kind is open. Resolved when chosen, never stored (DESIGN.txt, "OFFER KINDS")."""
    for offer in rules.offers:
        if offer.kind == verb.kind and is_shown(save, rules, offer.id) and not is_answered(save, rules, offer.id):
            return next((AnswerOffer(offer.id, a.id) for a in offer.answers if a.role == verb.role), None)
    return None


def acting(save: Save, rules: Rules, verb: AnswerOffer | AnswerKind) -> AnswerOffer | None:
    """The AnswerOffer an answering order's verb applies now, or None when it cannot act."""
    if isinstance(verb, AnswerKind):
        return resolved(save, rules, verb)
    return verb if can_answer(save, rules, verb) else None


def answer_card(answer: AnswerDef) -> CardId | None:
    """The card an answer sets running: the first its outcome queues, else its first install's, else the first it
    starts, else None. Read off the rule, so the engine holds no presentation field."""
    o = answer.outcome
    return next(iter((*o.queues, *(i.card for i in o.orders), *o.starts)), None)
