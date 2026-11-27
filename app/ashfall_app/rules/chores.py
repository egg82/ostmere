"""Which chips are a season's chores (docs/decisions/clock.md, "Each season brings its own chores"): one reading, shared by
the retired-chores check (retire_checks.py) and the page's hint on a chore with no order card (api ChipInfo.chore)."""
from typing import TYPE_CHECKING

from ..engine import AtLeast, AtMost, ChipId, Rules, StoreValue

if TYPE_CHECKING:
    from .schema import Opening


def chores(o: "Opening", rules: Rules) -> list[ChipId]:
    """The chips watching a store that has a maker, every one of them (cards and standing actions alike) a standing
    action some season's turn unlocks."""
    seasonal = {u.id for t in o.triggers if t.season for u in t.outcome.unlocks if u.unlock_kind == "action"}
    found: list[ChipId] = []
    for chip in rules.chips:
        when = chip.when
        if not isinstance(when, (AtLeast, AtMost)) or not isinstance(when.subject, StoreValue):
            continue
        store = when.subject.store
        makers = {str(a.id) for a in rules.standing if any(f.store == store for f in a.makes)}
        makers |= {str(c.id) for c in rules.cards if any(f.store == store for f in c.makes)}
        if makers and makers <= seasonal:
            found.append(chip.id)
    return found
