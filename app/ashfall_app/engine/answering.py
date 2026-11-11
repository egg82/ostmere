"""Answering an offer: the two unlocks, then the answer's outcome as a trigger's lands. Semantics: DESIGN.txt,
"AnswerOffer"."""
from dataclasses import replace

from .answers import AnswerOffer
from .ids import LineKey
from .index import index
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind, unlock_key
from .work import apply_outcome


def answered(save: Save, rules: Rules, verb: AnswerOffer) -> tuple[Save, tuple[LineKey, ...]]:
    """`verb` applied to a save where it can act (offerstate.can_answer): Unlock(ANSWERED) and Unlock(ANSWER) join
    save.unlocked whatever rules.opening is, then the answer's outcome lands in field order; its lines are returned
    (the caller emits them with card None). Orders and the queue evaluate after it."""
    given = {Unlock(UnlockKind.ANSWERED, verb.offer), Unlock(UnlockKind.ANSWER, verb.answer)}
    save = replace(save, unlocked=tuple(sorted(set(save.unlocked) | given, key=unlock_key)))
    return apply_outcome(save, rules, index(rules).answers[verb.answer][1].outcome)
