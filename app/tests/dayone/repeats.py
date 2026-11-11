"""No line is logged twice in a save unless its source runs again on purpose. Across a day-one play, from the opening's
start, each line key is logged at most once, except one every occurrence of which was written by a card with no cap: a
repeat task, whose absent cap is the explicit field saying it runs again (engine cards.py, CardDef.lines). A chip's and
a trigger's lines name no card, so they are held to once.

Problems name the key, its sources and the count, ids only (CLAUDE.md, "Never spoil the owner")."""
from collections import defaultdict
from collections.abc import Iterable

from ashfall_app.engine import Line, Rules


def repeated(rules: Rules, lines: Iterable[Line]) -> list[str]:
    """One problem per line key logged more than once whose occurrences are not all a repeat task's."""
    uncapped = {c.id for c in rules.cards if c.cap is None}
    sources: dict[str, list[str | None]] = defaultdict(list)
    for line in lines:
        sources[line.key].append(line.card)
    return [f"{key} logged {len(found)} times, from {sorted({s or 'no card' for s in found})}"
            for key, found in sorted(sources.items())
            if len(found) > 1 and not all(s is not None and s in uncapped for s in found)]
