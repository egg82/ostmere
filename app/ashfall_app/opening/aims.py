"""The check on an Opening's aims (feature_entries.AimEntry; docs/decisions.md, "Every stretch of play has a stated aim").
Raises ValueError naming the aim. Imports the schema for types only (checks.py calls this)."""
from typing import TYPE_CHECKING

from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening

AIM_MAX_CHARS = 40
"""An aim is one line at the band's top: at a phone's 390 px it holds about fifty characters at its size."""


def check_aims(o: "Opening") -> None:
    """One aim always set: the first holds from the start, each later one from an unlock the start or some outcome
    really gives (so the aim before it ends); each fits one line."""
    if not o.aims:
        fail("aims", "needs an aim from the start: every stretch of play has one")
    if o.aims[0].after is not None:
        fail(f"aim {o.aims[0].id}", "the first aim holds from the start, so it takes no after")
    given = {(u.unlock_kind, u.id) for u in o.start}
    given |= {(u.unlock_kind, u.id) for _, out in outcomes(o) for u in out.unlocks}
    for a in o.aims[1:]:
        if a.after is None:
            fail(f"aim {a.id}", "only the first aim takes no after")
        if (a.after.unlock_kind, a.after.id) not in given:
            fail(f"aim {a.id}", f"nothing unlocks {a.after.unlock_kind} {a.after.id}, so the aim before it never ends")
    for a in o.aims:
        if len(o.text.get(a.text_key, "")) > AIM_MAX_CHARS:
            fail(f"aim {a.id}", f"over {AIM_MAX_CHARS} characters: it must fit one line on a phone")
