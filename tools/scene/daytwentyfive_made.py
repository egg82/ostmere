"""Day twenty-five's built thing: the midden pit, dug on open ground near the hall. Time Fantasy's: the hole is the
Hometown pack's dirt hole and the spoil its small mound (1x, doubled to the scene's grain), both graded to the world's
dark soil. Nothing is drawn.
Story spoilers (content/team/week-four.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

import kit
from daytwo import cut
from place import canvas, put
from tints import SOIL

HOMETOWN = "hometown_TFcolor_update_8.24/_tfrecolor_8.24/master_everything.png"
HOLE, MOUND = (564, 644, 573, 652), (580, 644, 589, 652)
"""The pack's dirt hole and its small mound, beside it on the same row (1x)."""
PIT = (586, 262)
"""The pit's bottom-left: open ground before the hall, between the people at its door and the woodshed."""


def midden_pit() -> Image.Image:
    hole, mound = (kit.up(kit.grade(cut(HOMETOWN, box), **SOIL)) for box in (HOLE, MOUND))
    out = canvas()
    put(out, hole, PIT[0], PIT[1] - hole.height)
    put(out, mound, PIT[0] + hole.width + 4, PIT[1] - mound.height + 2)
    return out
