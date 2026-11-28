"""Day thirty-one's made things and the cat, all Time Fantasy's: the bar the larder's door was shut with, leaning on the
hall's wall by its doorway (Farm and Fort's spear shaft, as day three's staff, in the camp's wood grade); the iron latch
on the doorway's post (the hasp of Hometown's banded plank door, 1x, doubled to the scene's grain, in a
cold iron grey); the cat on the hall's ridge (Animals' grey cat, its front view, at its own grain, in the world's cool
grade). Nothing is drawn.

Story spoilers (content/team/week-five.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

from day_four.dayfour_creatures import WORLD
from day_three.daythree_poses import staff
from day_two.daytwo import cut
from draw import kit
from draw.place import canvas, put
from draw.tints import WOOD

DOORS = "hometown_TFcolor_update_8.24/_tfrecolor_8.24/1X/characters/!doors1a.png"
HASP = (122, 18, 127, 22)
"""The banded door's iron hasp and its staple (1x): what is fitted to a doorpost."""
IRON = kit.Grade(sat=0.1, mul=(0.95, 0.97, 1.0), bright=0.85, contrast=1.15)
"""The bands' blue taken to cold iron."""
LATCH_AT = (721, 198)
"""The hasp's top-left on the hall's doorway's right post (the doorway spans x 695-727, its foot at y 222)."""
BAR_FOOT = (684, 222)
"""The bar's foot against the hall's wall, left of the doorway."""
CATS = "animals1_shadowless/shadowless/animals1_shadowless.png"
CAT = (130, 144, 156, 180)
"""The grey cat facing down, its middle frame (1x): the sheet's second cat block, the front-view row."""
CAT_FEET = (676, 140)
"""On the hall's ridge beam (y 137-145), left of the chimney, looking down into the yard."""


def bar() -> Image.Image:
    shaft = kit.grade(staff(), **WOOD).rotate(-12, expand=True)
    out = canvas()
    put(out, shaft, BAR_FOOT[0] - shaft.width, BAR_FOOT[1] - shaft.height)
    return out


def latch() -> Image.Image:
    out = canvas()
    put(out, kit.up(kit.grade(cut(DOORS, HASP), **IRON)), *LATCH_AT)
    return out


def cat() -> Image.Image:
    sprite = kit.grade(cut(CATS, CAT), **WORLD)
    out = canvas()
    put(out, sprite, CAT_FEET[0] - sprite.width / 2, CAT_FEET[1] - sprite.height)
    return out
