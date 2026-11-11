"""Day twelve's found world, cool: the bear's sign on the felled birch (its shelves torn down, claw marks scored in the
wood) and the wolf that sits at the edge of the light. Pieces are Time Fantasy's: the shelves are day eight's (the cave
plants'), the wolf week 1's Monsters wolf in its seated back view, a lighter grey than the pack. Drawn are the claw
marks, which the kit has none of.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

import random

from PIL import Image, ImageChops

import dayeight_world as d8world
import kit
from dayfour_creatures import wolf
from place import canvas, put

SEED = 112
GREY = kit.Grade(sat=0.15, mul=(0.95, 0.97, 1.02), bright=0.72, contrast=1.1)
"""The white wolf taken to a mid grey, paler than the pack's dark pelt, its eyes kept."""
SITS = (150, 287)
"""Where it sits: at the light's edge below the smoke rack, where week 1's wolf stood, its back to us."""
GOUGE, SCORE = (214, 178, 128, 255), (50, 52, 58, 255)
"""The stump's own colours: the warm of its cut wood, where the claws went in, and its darkest bark, the gouge's
shaded side."""


def sitter() -> Image.Image:
    """The wolf's back view, which the sheet draws upright on its haunches: sat, facing the fire."""
    return wolf("up", SITS, coat=GREY)


def torn(log: Image.Image, stump: Image.Image) -> Image.Image:
    """The shelves torn off the birch: one left on the trunk, the rest broken on the ground under it."""
    lb, sb = log.getchannel("A").getbbox(), stump.getchannel("A").getbbox()
    assert lb is not None and sb is not None
    shelves = [d8world.shelf(b) for b in d8world.SHELVES]
    out = canvas()
    span = lb[2] - lb[0]
    put(out, shelves[0], lb[0] + 0.08 * span, lb[1] - shelves[0].height // 2)
    for i, f in enumerate((0.3, 0.55, 0.8)):
        s = shelves[(i + 1) % 3].rotate(180 if i % 2 else 0)
        put(out, s, lb[0] + f * span, lb[3] - s.height + 3)
    put(out, shelves[2].rotate(180), sb[0] - 2, sb[3] - 4)
    return out


def claw_marks(stump: Image.Image) -> Image.Image:
    """Three gouges raked slantwise down the stump's face from below its cut top, at the art's 1x grain: the cut
    wood's warm with the bark's darkest on the far side of each, kept inside the stump."""
    sb = stump.getchannel("A").getbbox()
    assert sb is not None
    small = Image.new("RGBA", (stump.width // 2, stump.height // 2))
    px = small.load()
    assert px is not None
    r = random.Random(SEED)
    x0, y0 = sb[0] // 2 + 1, sb[1] // 2 + 2
    cuts = [[(x0 + k * 2 + i // 3, y0 + i + k % 2) for i in range(4 + r.randrange(2))] for k in range(3)]
    for x, y in (p for cut in cuts for p in cut):
        px[x + 1, y] = SCORE
    for x, y in (p for cut in cuts for p in cut):
        px[x, y] = GOUGE
    out = kit.up(small)
    out.putalpha(ImageChops.multiply(out.getchannel("A"), stump.getchannel("A")))
    return out
