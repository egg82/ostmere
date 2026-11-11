"""Days four to seven's built things, warm because the camp made them: the woodshed in three stages, the second bay, the
turned ground (and a pelt over it for a night), the hearth stones round the pot, pelts pegged by the rack and laid in the
bays, and the spear leaning at the lean-to. Staged builds are additive layers, as day three's are.
Pieces are Time Fantasy's: the firewood stacks, the dirt mounds and the hide from the Farm and Fort and outside sheets,
the stones the Ashlands' loose rocks. What is drawn is the shed's poles and thatch, in the kit's manner, which the kit has no shed for.
Story spoilers (content/team/days-four-to-seven.md, Art): never shown to the owner."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageOps

import dayone
import daythree_made as day3
import kit
from daytwo import OUTSIDE, cut, hide_frame
from dayone import art, placed
from kit import ASH_B
from place import canvas, put
from tints import ACCENT

FARM = "tf_farmandfort/rpgmaker_VXa/tileB_farmA.png"
SHED = (346, 156)
"""The woodshed's top-left: below the woodstack at the wall stub, right of the watch fire, clear of the scrub."""
BAY2 = (70, 247)
"""The second bay's top-left: beside the first, its open side to the left."""
TURNED = (374, 204)
"""The turned ground's top-left: on the ground the hearth's warmth reaches, right of the stool."""
POT_STONES = (312, 229)
"""Where the hearth stones ring the pot: its base on the hearth's rim."""
PEGGED = [(142, 272), (172, 273)]
"""Where pelts are pegged out flat on the ground under the rack."""
BAY_FLOORS = [(22, 266), (79, 266), (24, 228)]
"""A pelt's place on each floor, in the order pelts are laid: the first bay, the second, the lean-to."""
SPEAR_FOOT = (72, 246)


def woodshed(stage: int) -> Image.Image:
    """Stage 1 the kit's posts and the beam across them; 2 the split firewood stacked under it, ends out; 3 the brush
    thatch on its poles."""
    if stage == 1:
        img, d = art(32, 22)
        for x in (1, 27):
            dayone.post(d, x, 5, 21)
        dayone.rail(d, 1, 30, 4)
        return placed(img, SHED)
    if stage == 2:
        out = canvas()
        pyramid, pair = (cut(OUTSIDE, (224, 193, 254, 223)), cut(OUTSIDE, (224, 229, 254, 256)))
        base = SHED[1] + 42
        put(out, pyramid, SHED[0] + 4, base - pyramid.height)
        put(out, pair, SHED[0] + 32, base - pair.height)
        return out
    return placed(dayone.gable(36, 12, 51), (SHED[0] - 4, SHED[1] - 20))


def bay2() -> Image.Image:
    """The first bay's roof of poles and brush, turned the other way."""
    first = day3.bay()
    box = first.getchannel("A").getbbox()
    assert box is not None
    out = canvas()
    put(out, ImageOps.mirror(first.crop(box)), BAY2[0], BAY2[1])
    return out


MOUNDS = [(421, 452, 445, 476), (450, 452, 473, 476), (485, 452, 508, 476)]
"""The Farm and Fort sheet's three dark soil mounds."""


def turned(stage: int) -> Image.Image:
    """Row `stage` of the turned ground: three clods of the pack's soil mound in a staggered row, one more row a stage."""
    mounds = [cut(FARM, box) for box in MOUNDS]
    out = canvas()
    rng = random.Random(60 + stage)
    for i in range(3):
        m = mounds[rng.randrange(3)]
        put(out, m, TURNED[0] + i * 21 + (stage % 2) * 6, TURNED[1] + (stage - 1) * 11)
    return out


def hide() -> Image.Image:
    """The hide off Farm and Fort's stretched-hide frame, laces and all."""
    return hide_frame().crop((17, 9, 44, 38))


def _flat(sprite: Image.Image) -> Image.Image:
    """Laid flat: every second row of it."""
    return kit.resize(sprite, (sprite.width, sprite.height // 2))


def turned_pelt() -> Image.Image:
    """A hide laid over the turned ground's near end for the night."""
    out = canvas()
    put(out, _flat(hide()), TURNED[0] + 48, TURNED[1] + 14)
    return out


def pegged(n: int) -> Image.Image:
    """The first pelt pegged out under the rack; the second beside it."""
    out = canvas()
    put(out, _flat(hide()), *PEGGED[n - 1])
    return out


def pelt_in_bay(n: int) -> Image.Image:
    """The nth pelt on a floor of the first bay, the second bay and the lean-to in turn."""
    out = canvas()
    put(out, _flat(hide()), *BAY_FLOORS[n - 1])
    return out


def hearth_stones(stage: int) -> Image.Image:
    """Three more stones a stage round the pot's base, the Ashlands' loose rocks in the stones' bright grey."""
    sheet = kit.load(ASH_B)
    out = canvas()
    for i in range(9):
        if i % 3 != stage - 1:
            continue
        angle = i * 40 + 20
        stone = kit.tile(sheet, 0 if i % 2 else 3, 2)
        stone = stone.crop(stone.getchannel("A").getbbox())
        stone = kit.resize(stone, (stone.width * 2 // 3, stone.height * 2 // 3))
        x = POT_STONES[0] + 21 * math.cos(math.radians(angle)) - stone.width / 2
        y = POT_STONES[1] + 7 * math.sin(math.radians(angle)) - stone.height / 2
        put(out, stone, x, y)
    return kit.grade(out, **ACCENT)


def spear_leaning() -> Image.Image:
    """The Farm and Fort long spear, head and all, leaned against the lean-to's front post."""
    shaft = cut(FARM, (193, 384, 217, 428)).rotate(12, expand=True, resample=Image.Resampling.NEAREST)
    out = canvas()
    put(out, shaft, SPEAR_FOOT[0] - shaft.width / 2, SPEAR_FOOT[1] - shaft.height)
    return out

