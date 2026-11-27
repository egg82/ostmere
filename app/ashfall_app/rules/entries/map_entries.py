"""The content file's places on the world map (api/contract/map.txt, "MAP"), as Type Objects."""
from typing import Literal

from .entries import Entry, UnlockEntry

type Stamp = Literal["village", "town", "city", "fort", "stronghold", "hill_village", "crossing", "mountain", "range",
                     "forest", "tree"]
"""The kind of stamp a place is drawn with. Closed: each kind is art the page owns (tools/mapstamps.py), so a new one is
art and page work as well as content."""

MAP_REACH = 8
"""The farthest a place lies from the town, in cells each way."""


class PlaceEntry(Entry):
    """One place on the world map, drawn once view.unlocked holds `reveal`. `at` is [east, north] in whole cells from the
    town at [0, 0]: roughly where, since the page places the art."""

    id: str
    stamp: Stamp
    at: tuple[int, int]
    reveal: UnlockEntry
    label_key: str | None = None
    """None for a place drawn unnamed (a forest, a range)."""
    labelled_after: UnlockEntry | None = None
    """When set, the place is drawn unlabelled until this unlock is held, then takes its label_key. A reveal's kinds."""
    over: str | None = None
    """The id of the place whose cell this one shares, drawn as a stamp on its stamp: the only way two places hold one cell."""
