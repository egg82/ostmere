"""Whether an id is unlocked. A leaf below gates and mixruns, which both read it."""
from .memo import PartsMemo
from .rules import Rules
from .state import Save
from .unlocks import PRESENT_ONLY, Unlock

_UNLOCKED: PartsMemo[frozenset[Unlock]] = PartsMemo()
"""Kept while the save's unlock set is the same tuple: the instants of an advance mostly unlock nothing."""


def is_unlocked(save: Save, rules: Rules, u: Unlock) -> bool:
    """With rules.opening None every unlock counts as held, but ANSWERED and ANSWER, which count only when present."""
    if rules.opening is None and u.kind not in PRESENT_ONLY:
        return True
    return u in _UNLOCKED.get((save.unlocked,), lambda: frozenset(save.unlocked))
