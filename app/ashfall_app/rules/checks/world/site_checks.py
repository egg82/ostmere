"""Where a card's work is shown (`site` on a card, entries.SiteEntry): a card and the card it is a twin of name the same site,
so the player's job and the town's version of it stand in one place. Structural fields only, never ids or words. Raises
ValueError naming the card (refs.fail). The layer a site names is checked against the scene in app/tests/test_scene_sites.py."""
from typing import TYPE_CHECKING

from ...refs import fail

if TYPE_CHECKING:
    from ...entries.entries import CardEntry
    from ...schema import Opening


def check_sites(o: "Opening") -> None:
    cards = {c.id: c for c in o.cards}
    for c in o.cards:
        twin = cards.get(c.twin_of) if c.twin_of is not None else None
        if twin is not None and c.site != twin.site:
            fail(f"card {c.id}", f"site differs from its twin_of {twin.id}: a job and its town twin are done at one place")


def unsited(o: "Opening") -> list["CardEntry"]:
    """The cards that say neither a site layer nor why they have none."""
    return [c for c in o.cards if c.site is None]
