"""Every card the player taps says what it is for: a presentation "action" card, a town twin included, has an
upside_key, except the plain gatherers below, whose face already shows a store the player spends directly. A twin is
excused by its twin_of being listed, so a lane's copy of a listed card needs no entry. Ids and fields only, never
text. Raises ValueError naming the cards (refs.fail)."""
from typing import TYPE_CHECKING

from ...refs import fail

if TYPE_CHECKING:
    from ...schema import Opening

BARE = frozenset({"gather_wood", "woodcutting", "scavenge", "forage", "rest"})


def check_upsides(o: "Opening") -> None:
    missing = [c.id for c in o.cards if c.presentation == "action" and c.upside_key is None
               and (c.twin_of or c.id) not in BARE]
    if missing:
        fail(f"cards {', '.join(missing)}", "are tapped by the player and say nothing of what they are for: each has "
                                            "an upside_key, or its id is in upside_checks.BARE")
