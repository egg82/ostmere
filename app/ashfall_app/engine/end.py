"""The end: recorded once, at the first resolved instant where rules.end is unlocked.

Semantics: DESIGN.txt, "The end". Every instant the engine resolves (new_save's, each event instant, a decision's) ends
here, and the unlock set changes only at such instants, so the first one the feature is unlocked at is when it first is.
"""
from dataclasses import replace

from .gates import is_unlocked
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind


def with_end(save: Save, rules: Rules) -> Save:
    """`save` with ended_at set to its time if the end holds now and was not yet recorded; else `save` unchanged."""
    if save.ended_at is not None or rules.end is None:
        return save
    if not is_unlocked(save, rules, Unlock(UnlockKind.FEATURE, rules.end)):
        return save
    return replace(save, ended_at=save.time)
