"""Day three's built things, warm because the camp made them: the larder's stone floor, the smoke rack's roof, the
raised bed and the bay against the lean-to. Each staged build is drawn as additive layers (`stage` 1..n draws only what
that stage adds), so a stage's layer shows from its push and the earlier ones stay under it.
Drawn at the packs' 1x grain in day one's palette and scaled with NEAREST.
Story spoilers (content/team/day-three.md, Art): never shown to the owner."""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

import dayone
import kit
from dayone import (RACK, STONE_GAP, STONE_PALE, STONE_TOP, WOOD_HI, WOOD_LINE, WOOD_MID,
                    art, placed)
from daytwo import cut

FLOOR = (140, 176)
"""The larder's floor, top-left in scene pixels: flagstones laid round and behind the larder and spilling right."""
FLOOR_SIZE = (84, 28)
BED = (8, 166)
"""The raised bed's top-left: the open ground above the lean-to, under the roof's shadow."""
BAY = (5, 240)
"""The bay's top-left: against the lean-to's foot, its roof joining the lean-to's."""
Cell = tuple[int, int, int, int]


def _cells(rng: random.Random, w: int, h: int, rows: tuple[int, ...]) -> list[Cell]:
    """Flagstone cells (x, y, w, h) in 1x pixels, in courses of the given heights, widths 6 to 9."""
    out: list[Cell] = []
    y = 0
    for row_h in rows:
        x = -rng.randrange(4)
        while x < w:
            cw = rng.randint(7, 11)
            out.append((max(x, 0), y, min(x + cw - 1, w - 1), y + row_h - 1))
            x += cw
        y += row_h
    return out


def _flagstone(d: ImageDraw.ImageDraw, cell: Cell, rng: random.Random) -> None:
    """A flat stone seen from above, one of the larder's own field stones laid down: its pale grey a step darker than
    the wall's (lying flat, it catches less light), lit along its far edge, its corners rounded off, set in the
    larder's dark joint under and beside it."""
    x0, y0, x1, y1 = cell
    if x1 - x0 < 3:
        return
    tone = rng.choice((-34, -28, -22, -16))
    d.rectangle((x0, y0, x1, y1), fill=STONE_GAP)
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=tuple(c + tone for c in STONE_PALE[:3]) + (255,))
    d.line((x0 + 1, y0, x1 - 2, y0), fill=tuple(c + tone for c in STONE_TOP[:3]) + (255,))
    d.point([(x0, y1 - 1), (x1 - 1, y1 - 1)], fill=STONE_GAP)
    if x1 - x0 > 7 and rng.random() < 0.5:
        d.point((rng.randint(x0 + 2, x1 - 3), y1 - 2), fill=tuple(c + tone - 16 for c in STONE_PALE[:3]) + (255,))


def larder_floor(stage: int) -> Image.Image:
    """Flagstones round the larder's foot. The stage takes the cells in its third of the way out from the larder's
    middle, so the floor spreads as it is laid."""
    w, h = FLOOR_SIZE[0] // 2, FLOOR_SIZE[1] // 2
    rng = random.Random(22)
    cells = [c for c in _cells(rng, w, h, (4, 4, 4, 3)) if _inside(c, w, h) and rng.random() < 0.8]
    ranked = sorted(cells, key=lambda c: _from_middle(c, w, h))
    n = len(ranked)
    img, d = art(w, h)
    for c in ranked[(stage - 1) * n // 3: stage * n // 3]:
        _flagstone(d, c, rng)
    return placed(img, FLOOR)


def _from_middle(c: Cell, w: int, h: int) -> float:
    return ((c[0] + c[2]) / 2 - w * 0.3) ** 2 / 4 + ((c[1] + c[3]) / 2 - h * 0.4) ** 2


def _inside(c: Cell, w: int, h: int) -> bool:
    cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
    return ((cx - w * 0.5) / (w * 0.52)) ** 2 + ((cy - h * 0.5) / (h * 0.55)) ** 2 <= 1


ROOF_BASE = (RACK[0] // 2 + 1, RACK[1] // 2 - 9)
"""The roof's eaves in 1x pixels: over the rack's two frames, nine pixels above their tops."""
ROOF_SPAN = 34


def rack_roof(stage: int) -> Image.Image:
    """A gable over the smoke rack on two posts. Stage 1 is the poles (the kit's posts and rafters); stage 2 the brush
    thatch laid on them, a gap left at the ridge for the smoke."""
    img, d = art(ROOF_SPAN + 4, 22)
    ex, ey, apex = 2, 10, (ROOF_SPAN // 2 + 2, 1)
    if stage == 1:
        for x in (ex - 1, ex + ROOF_SPAN - 3):
            dayone.post(d, x, ey, 21)
        dayone.rafter(d, (ex - 1, ey + 1), (apex[0], apex[1] + 1))                   # under the thatch's edges
        dayone.rafter(d, (apex[0], apex[1] + 1), (ex + ROOF_SPAN, ey + 1))
    else:
        img.alpha_composite(dayone.gable(ROOF_SPAN + 4, ey + 2 - apex[1], 31), (0, apex[1]))
        d.rectangle((apex[0] - 1, apex[1], apex[0] + 1, apex[1] + 1), fill=(0, 0, 0, 0))   # the smoke's gap
    return placed(img, (ROOF_BASE[0] * 2 - 4, ROOF_BASE[1] * 2 - 2))


def raised_bed(stage: int) -> Image.Image:
    """Stage 1 a frame of the kit's poles (outlined, lit along the top) on four posts; 2 a stone footing along its
    front; 3 the bed: Farm and Fort's loose hay heaped inside the frame, its front rail over it, a rolled hide at the
    head."""
    img, d = art(30, 16)
    if stage == 1:
        dayone.rail(d, 1, 28, 5)
        for x in (0, 26):
            dayone.post(d, x, 2, 15)
        dayone.rail(d, 1, 28, 9)
    elif stage == 2:
        for x in range(1, 29, 4):
            d.rectangle((x, 12, x + 3, 14), fill=STONE_PALE, outline=STONE_GAP)
            d.line((x, 12, x + 2, 12), fill=STONE_TOP)
    else:
        hay = cut(FF_SHEET, HAY)
        img.alpha_composite(hay.crop((0, 0, hay.width, 9)), (4, 1))               # what shows over the front rail
        img.alpha_composite(kit.pixels(*HIDE_ROLL), (4, 4))
        dayone.rail(d, 1, 28, 9)
        for x in (0, 26):
            dayone.post(d, x, 8, 15)
    return placed(img, BED)


FF_SHEET = "tf_farmandfort/ff_master_tile_sheet.png"
HAY = (515, 177, 540, 190)
"""Farm and Fort's loose hay pile (1x), the low wide one."""
HIDE_ROLL = ([".nnnnnn.", "nphhhhhn", "npplllln", "nphmmmmn", ".nnnnnn."],
             {"n": dayone.NAVY, "p": WOOD_LINE, "h": WOOD_HI, "l": (177, 124, 84, 255), "m": WOOD_MID})
"""A hide rolled up, end on at the left, in the colours of the kit's brown bedroll."""


def bay() -> Image.Image:
    """A second, lower lean-to against the lean-to's foot, open to the right."""
    return placed(dayone.shelter(34, 21, 13), BAY)
