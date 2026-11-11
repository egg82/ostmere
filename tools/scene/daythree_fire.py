"""Day three's fires: the clay hearth built up round the camp's fire in courses, the stew pot Time Fantasy's cooking
frame carries, and the watch fire's ring at the gap (laid, then lit), its stones and flames the camp fire's own sprites
at half size.
Story spoilers (content/team/day-three.md, Art): never shown to the owner."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

import kit
from dayone import CAMP, art
from kit import T
from parts import campfire_split
from place import FIRE, H, W, canvas, put

CLAY_HI, CLAY, CLAY_DK, CLAY_SHADE, MORTAR, OUTLINE = ((198, 153, 91, 255), (179, 117, 75, 255), (157, 95, 62, 255),
                                                     (125, 86, 67, 255), (108, 60, 74, 255), (53, 64, 72, 255))
"""Time Fantasy's brick fireplace's ramp: its bricks lit, body and shade, the shade inside its arch, its mortar, its outline."""
HEARTH_R = (22, 12)
"""The hearth's wall on the floor, half-width and half-depth in 1x pixels, round the fire's ring."""
COURSE = 3
"""One course's height in 1x pixels; a stage lays one more (the last two, with the rim)."""
WATCH = (9.4 * T, 5.55 * T)
"""The watch fire's centre: just inside the gap, on the camp side, facing the track."""
WATCH_SCALE = 0.7
POT_AT = (FIRE[0] + 0.85 * T, FIRE[1] - 0.45 * T)
"""The pot's top-left: on the hearth's rim at the fire's right, clear of the stool."""


def _arc(x: int, r: tuple[int, int]) -> float:
    """How far below the ellipse's middle its edge lies at column x (half the depth at most)."""
    return r[1] * math.sqrt(max(0.0, 1 - (x / r[0]) ** 2))


def hearth(stage: int) -> Image.Image:
    """A wall of clay bricks round the fire's ring, a course a stage, drawn as Time Fantasy draws its brick fireplace:
    its outer face in courses of bricks lit from above with mortar between, the inside of the far wall in shade, and the
    flat top of the wall so far, outlined inside and out."""
    rx, ry = HEARTH_R
    inner = (rx - 3, ry - 2)
    top = 3 * COURSE
    img, d = art(2 * rx + 3, 2 * ry + top + 4)
    cx, cy = rx + 1, ry + top + 1
    lo, hi = (stage - 1) * COURSE, stage * COURSE
    for x in range(-rx, rx + 1):
        for h in range(lo, hi):
            d.point((cx + x, cy - h + _arc(x, HEARTH_R)), fill=_lump(x, h))
        if lo == 0:
            d.point((cx + x, cy + 1 + _arc(x, HEARTH_R)), fill=OUTLINE)          # the foot's outline
    for x in range(-inner[0], inner[0] + 1):
        for h in range(lo, hi):
            d.point((cx + x, cy - h - _arc(x, inner)), fill=CLAY_SHADE if h % COURSE else MORTAR)
    _rim(d, cx, cy - hi, inner)
    for h in range(lo, hi + 1):
        for x in (-rx - 1, rx + 1):
            d.point((cx + x, cy - h), fill=OUTLINE)                              # the wall's ends, outlined
    out = canvas()
    put(out, kit.up(img), FIRE[0] - (cx + 0.5) * 2, FIRE[1] - (cy + 0.5) * 2)
    return out


def _lump(x: int, h: int) -> tuple[int, int, int, int]:
    """The outer face at column x, height h: bricks six wide, each course's set half a brick from the last, mortar
    under each course and between bricks, a brick's top row lit and its right end in shade."""
    course, row = divmod(h, COURSE)
    shift = (x + 30 + course * 3) % 6
    if row == 0 or shift == 0:
        return MORTAR
    if shift == 5:
        return CLAY_DK
    return CLAY_HI if row == COURSE - 1 else CLAY


def _rim(d: ImageDraw.ImageDraw, cx: int, ty: int, inner: tuple[int, int]) -> None:
    """The wall's flat top: lit on the far side, the clay's own tone on the near, an outline along both edges."""
    rx = HEARTH_R[0]
    for x in range(-rx, rx + 1):
        near, far = ty + _arc(x, HEARTH_R), ty - _arc(x, HEARTH_R)
        for y in range(int(far), int(near) + 1):
            inside = abs(x) <= inner[0] and ty - _arc(x, inner) < y < ty + _arc(x, inner)
            if not inside:
                d.point((cx + x, y), fill=CLAY_HI if y < ty else CLAY)
        d.point((cx + x, int(far) - 1), fill=OUTLINE)
        if abs(x) <= inner[0]:
            d.point((cx + x, int(ty - _arc(x, inner))), fill=OUTLINE)
            d.point((cx + x, int(ty + _arc(x, inner))), fill=CLAY_SHADE)


def pot() -> Image.Image:
    """The iron pot off Time Fantasy's cooking frame (its hook cut away), set on the hearth's rim."""
    sheet = kit.load(CAMP).crop((34, 276, 47, 288))
    sprite = kit.up(sheet)
    out = canvas()
    put(out, sprite, POT_AT[0], POT_AT[1])
    return out


def _watch_piece(sprite: Image.Image) -> Image.Image:
    box = sprite.getchannel("A").getbbox()
    assert box is not None
    sprite = sprite.crop(box)
    return kit.resize(sprite, (round(sprite.width * WATCH_SCALE), round(sprite.height * WATCH_SCALE)))


def _at_watch(sprite: Image.Image) -> Image.Image:
    out = canvas()
    put(out, sprite, WATCH[0] - sprite.width / 2, WATCH[1] - sprite.height / 2)
    return out


def watch_ring() -> Image.Image:
    """The ring of stones, the camp fire's at half size."""
    ring, _ = campfire_split("camp_campfire_unlit")
    return _at_watch(_watch_piece(ring))


def watch_laid() -> Image.Image:
    """Kindling laid in it."""
    _, laid = campfire_split("camp_campfire_unlit")
    return _at_watch(_watch_piece(laid))


def watch_lit() -> Image.Image:
    """The same, burning."""
    _, lit = campfire_split("camp_campfire_lit")
    return _at_watch(_watch_piece(lit))


def watch_light() -> Image.Image:
    """A small warm light on the ground round it, for a screen blend."""
    mask = kit.radial((W, H), WATCH, 1.9 * T, 150, 0, squash=0.8)
    light = Image.new("RGBA", (W, H), (150, 78, 26, 255))
    light.putalpha(mask)
    return light

