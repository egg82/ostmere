"""The world map on the wire (CONTRACT.txt, "MAP"): the content's places. Whether one is revealed is view.unlocked's.
Re-exported from content_models.py."""
from enum import StrEnum

from pydantic import BaseModel

from .models import Unlock


class Stamp(StrEnum):
    """The kind of stamp a place is drawn with: each is art the page owns (/assets/art/map/manifest.json)."""

    VILLAGE = "village"
    TOWN = "town"
    CITY = "city"
    FORT = "fort"
    STRONGHOLD = "stronghold"
    HILL_VILLAGE = "hill_village"
    CROSSING = "crossing"
    MOUNTAIN = "mountain"
    RANGE = "range"
    FOREST = "forest"
    TREE = "tree"


class PlaceInfo(BaseModel):
    """A place on the world map, in content order: drawn once view.unlocked holds `reveal`, at whole cells east and north
    of the town (which stands at 0, 0)."""

    place: str
    stamp: Stamp
    east: int
    north: int
    reveal: Unlock
    label_key: str | None
    """The place's name; null for a place drawn unnamed."""
