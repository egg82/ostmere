"""What an open offer's answers do to the lasting changes they make (design/townsfolk.txt, "Answer shifts"). Reads only."""
from .gates import effective_stack
from .modifiers import change_bp, total_change_bp
from .offers import AnswerDef
from .rules import Rules
from .state import Save
from .viewparts import AnswerShift


def answer_shifts(save: Save, rules: Rules, answer: AnswerDef) -> tuple[AnswerShift | None, ...]:
    """One shift per distinct change among the answer's modifiers, in authored order (the order of the answer's
    change_bp on the wire): each target's total change now and with the answer's entries on the stack. None where the
    entries of one change aim at targets that stand differently now or would after."""
    stack = effective_stack(save, rules)
    later = stack + answer.outcome.modifiers
    slots: dict[int, set[AnswerShift]] = {}
    for m in answer.outcome.modifiers:
        slots.setdefault(change_bp(m), set()).add(AnswerShift(total_change_bp(stack, m.target), total_change_bp(later, m.target)))
    return tuple(next(iter(s)) if len(s) == 1 else None for s in slots.values())
