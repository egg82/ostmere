"""Every Leave part the rules hold, read by validation (planchecks) and by the stopped standings (gone). Reads the rules
alone, imported below rules.py, so it names Rules for type checking only."""
from typing import TYPE_CHECKING

from .cards import Leave

if TYPE_CHECKING:
    from .rules import Rules


def all_leaves(rules: "Rules") -> tuple[Leave, ...]:
    """The Leave parts of every outcome: cards' outcomes and finishes, triggers' and answers'."""
    outcomes = [o for c in rules.cards for o in (c.outcome, c.finished)] + [t.outcome for t in rules.triggers]
    outcomes += [a.outcome for x in rules.offers for a in x.answers]
    return tuple(leave for o in outcomes for leave in o.leaves)
