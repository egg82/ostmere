"""Day one's made things, warm because the player made them: the lean-to, the larder, the smoke rack with its meat, the snares. Drawn at the packs' 1x grain in the Farm and Fort wood's palette (or built
from its pieces) and scaled with NEAREST, so they sit in the art's pixels.
Story spoilers (content/team/day-one.md, Art): never shown to the owner.
"""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

import kit
from kit import T
from place import H, W, canvas, put

WOOD_HI, WOOD_LIGHT, WOOD_MID, WOOD_DARK, WOOD_LINE = (
    (199, 153, 92, 255), (184, 126, 80, 255), (157, 95, 62, 255), (125, 86, 67, 255), (108, 60, 74, 255))
STONE_PALE, STONE_TOP, STONE_GAP = (140, 138, 134, 255), (174, 172, 166, 255), (58, 56, 60, 255)
ROPE_HI, ROPE, ROPE_LOW = (222, 188, 112, 255), (184, 126, 80, 255), (108, 60, 74, 255)
"""The fort's braided rope's own ramp (tileB_fortA): the snares' cord is drawn in it, never in a paler cord."""
SHADOW = (30, 27, 30, 230)
NAVY, STRAW = (53, 64, 72, 255), (204, 170, 115, 255)
"""The kit's outline and dark (Farm and Fort draws its outlines and a tent's inside in it), and its thatch's pale straw."""
GROUND_SHADOW = (36, 36, 42, 130)
LARDER = (2.7 * T, 5.35 * T)
"""The larder's top-left: in front of the wall, left of the drying rail, where the prints end."""
RACK = (4.15 * T, 7.25 * T)
"""The smoke rack's top-left: between the lean-to and the fire, its smoke rising from the pole."""
LEAN_TO = (0.15 * T, 6.15 * T)
"""The lean-to's top-left, in the open ground below the roof's corner, its open side toward the gap."""
SNARES = [(13.55 * T, 6.95 * T), (14.3 * T, 7.6 * T), (13.75 * T, 8.25 * T)]
"""Where each snare's sapling stands, at the birch edge past the stump."""


def art(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w, h))
    return img, ImageDraw.Draw(img)


def placed(sprite: Image.Image, at: tuple[float, float]) -> Image.Image:
    img = canvas()
    put(img, kit.up(sprite), at[0], at[1])
    return img


def shelter(w: int, h: int, seed: int) -> Image.Image:
    """A lean-to seen from the side, at 1x, drawn as the kit draws its tents and posts: a thatch of brush on poles from
    the ground at the left up onto a forked post at the right, a ragged dark eave under it, outlined in the kit's navy;
    the navy dark under it open to the right with dry grass on its floor, a back pole inside, a shadow on the ash."""
    img, d = art(w, h)
    rng = random.Random(seed)
    ground, post, top, foot = h - 2, w - 6, 2, 1
    slope = (ground - top) / (post + 1 - foot)
    ridge = {x: round(top + (post + 1 - x) * slope) for x in range(foot, post + 2)}
    d.line((0, ground + 1, w - 1, ground + 1), fill=GROUND_SHADOW)
    for x in range(foot + 2, post + 1):
        d.line((x, ridge[x] + THATCH, x, ground), fill=NAVY)                           # the dark under the roof
    for x in range(foot + 6, post):
        d.point((x, ground), fill=rng.choice((WOOD_HI, STRAW, WOOD_LIGHT)))         # the grass bed
        if rng.random() < 0.5:
            d.point((x, ground - 1), fill=rng.choice((WOOD_HI, WOOD_LIGHT, WOOD_MID)))
    back = (foot + post) // 2 + 2
    d.line((back, ridge[back] + THATCH + 1, back, ground - 1), fill=WOOD_LINE)               # a back pole, inside
    _post(d, post, top, ground)
    for x in range(foot, post + 2):
        _thatch(d, rng, x, ridge[x], ground)
    d.point((foot - 1, ground), fill=NAVY)
    return img


def post(d: ImageDraw.ImageDraw, x: int, top: int, foot: int) -> None:
    """A standing pole as the kit draws one: two pixels of the wood's light and mid between navy lines, capped in navy
    at `top` and `foot`."""
    d.line((x, top, x, foot), fill=NAVY)
    d.line((x + 1, top + 1, x + 1, foot - 1), fill=WOOD_HI)
    d.line((x + 2, top + 1, x + 2, foot - 1), fill=WOOD_MID)
    d.line((x + 3, top, x + 3, foot), fill=NAVY)
    d.line((x + 1, top, x + 2, top), fill=NAVY)
    d.line((x + 1, foot, x + 2, foot), fill=NAVY)


def rail(d: ImageDraw.ImageDraw, x0: int, x1: int, y: int) -> None:
    """A pole laid across from x0 to x1 as the kit draws one: lit on top, shaded under, outlined in navy above and
    below."""
    d.line((x0, y - 1, x1, y - 1), fill=NAVY)
    d.line((x0, y, x1, y), fill=WOOD_HI)
    d.line((x0, y + 1, x1, y + 1), fill=WOOD_MID)
    d.line((x0, y + 2, x1, y + 2), fill=NAVY)


def rafter(d: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int]) -> None:
    """A pole laid on a slope from a to b, drawn as `rail` is: navy over its lit top, its shaded underside, navy under."""
    for dy, col in ((-1, NAVY), (0, WOOD_HI), (1, WOOD_MID), (2, NAVY)):
        d.line((a[0], a[1] + dy, b[0], b[1] + dy), fill=col)


def gable(w: int, h: int, seed: int) -> Image.Image:
    """A pitched roof of brush thatch from the front, at 1x, as the kit draws its round hut's straw: strands falling
    from the ridge, paler on the left where the light comes from, a ragged dark eave, all outlined in navy."""
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    mid = (w - 1) / 2
    shape = [(0, h - 1), (round(mid), 0), (w - 1, h - 1)]
    d.polygon(shape, fill=NAVY)
    px = img.load()
    assert px is not None
    for y in range(h):
        for x in range(w):
            if kit.rgba(px, x, y)[3]:
                px[x, y] = _straw(x, y, mid, h, rng)
    d.polygon(shape, outline=NAVY)
    return img


def _straw(x: int, y: int, mid: float, h: int, rng: random.Random) -> tuple[int, int, int, int]:
    """One pixel of a gable's thatch: strands four pixels long falling from the ridge, the right half a step darker,
    the bottom row the eave."""
    if y >= h - 2:
        return WOOD_DARK if rng.random() < 0.7 else WOOD_LINE
    run = random.Random(x * 97 + (y + x % 3) // 4 * 13).random()
    if x % 3 == 0 and run < 0.5:
        return WOOD_MID
    if x <= mid:
        return STRAW if run < 0.45 else WOOD_HI if run < 0.85 else WOOD_LIGHT
    return WOOD_HI if run < 0.4 else WOOD_LIGHT if run < 0.8 else WOOD_MID


def _post(d: ImageDraw.ImageDraw, x: int, top: int, ground: int) -> None:
    """The shelter's post, forked at the top."""
    post(d, x, top - 1, ground + 1)
    d.point([(x, top - 2), (x + 3, top - 2), (x + 4, top - 3)], fill=NAVY)
    d.point([(x + 1, top - 1), (x + 2, top - 1)], fill=WOOD_LINE)


THATCH = 6
"""The roof's depth in 1x pixels, outline to eave."""


def _thatch(d: ImageDraw.ImageDraw, rng: random.Random, x: int, y: int, ground: int) -> None:
    """One column of the roof from its ridge line down: the navy outline, rows of straw with the bundles' shaded seams
    running down the slope, the dark eave, now and then a strand hanging below it."""
    cols = [NAVY]
    for row in range(1, THATCH):
        run = random.Random((x + row * 2) // 3 * 31 + row).random()             # strands three pixels long
        if row == 1:
            cols.append(STRAW if run < 0.7 else WOOD_HI)
        elif (x + row * 2) % 3 == 0 and run < 0.5:
            cols.append(WOOD_MID)                                                  # the gap at a strand's end
        else:
            cols.append(WOOD_HI if run < 0.45 else STRAW if run < 0.7 else WOOD_LIGHT)
    cols.append(WOOD_DARK if rng.random() < 0.75 else WOOD_LINE)
    for row, c in enumerate(cols):
        if y + row <= ground:
            d.point((x, y + row), fill=c)
    if rng.random() < 0.35 and y + THATCH + 1 <= ground:
        d.point((x, y + THATCH + 1), fill=WOOD_LINE)


def roof_posts(eave_y: int, foot_y: int, xs: tuple[int, int]) -> Image.Image:
    """Two poles holding the roof's eave up at its ends, standing on the camp floor in front of the wall: the roof's
    covered corner is the space between them and the wall."""
    img, d = art(W // 2, H // 2)
    for x in xs:
        post(d, x // 2, eave_y // 2, foot_y // 2)
    return kit.up(img)


def lean_to() -> Image.Image:
    """The lean-to, its open side toward the gap and the ridge."""
    return placed(shelter(34, 25, 11), LEAN_TO)


def larder(wood: kit.Grade) -> Image.Image:
    """Dry-stone, three courses of pale field stones with dark gaps between, a plank lid weighted with a stone. The
    stones keep the world's cool grey (the layer is not baked); only the lid takes the made things' `wood` grade."""
    stones, d = art(28, 16)
    rng = random.Random(3)
    for row, y in enumerate((5, 9, 12)):
        x = -rng.randrange(4) + row % 2
        while x < 28:
            w = rng.choice((4, 5, 5, 6))
            x0, x1 = max(x, 0), min(x + w - 2, 27)
            if x1 - x0 >= 1:
                h = 2 + (rng.random() < 0.5)
                tone = rng.choice((-14, -6, 0, 6))
                d.rectangle((x0, y, x1, y + h), fill=tuple(c + tone for c in STONE_PALE[:3]) + (255,))
                d.line((x0, y, x1, y), fill=STONE_TOP)                             # light from above
                d.point([(x0, y + h), (x1, y + h)], fill=STONE_GAP)                # rounded lower corners
            x += w
    d.line((0, 15, 27, 15), fill=STONE_GAP)                                        # the bottom course's shadow
    lid, d = art(28, 16)
    d.rectangle((0, 2, 27, 5), fill=WOOD_LIGHT, outline=NAVY)
    d.line((1, 3, 26, 3), fill=WOOD_HI)
    d.point([(9, 4), (18, 4), (9, 3), (18, 3)], fill=WOOD_DARK)                    # seams between the planks
    lid = kit.grade(lid, **wood)
    d = ImageDraw.Draw(lid)
    d.rectangle((17, 0, 21, 2), fill=STONE_TOP, outline=STONE_GAP)                 # the stone on the lid
    wall, _ = art(28, 16)
    ImageDraw.Draw(wall).rectangle((0, 5, 27, 15), fill=STONE_GAP)                # the gaps between the stones
    wall.alpha_composite(stones)
    wall.alpha_composite(lid)
    return placed(wall, LARDER)


def ghost(img: Image.Image, opacity: float = 0.4) -> Image.Image:
    """A thing at `opacity`: what is being built, shown at its spot while the build runs."""
    out = img.copy()
    out.putalpha(Image.eval(img.getchannel("A"), lambda v: int(v * opacity)))
    return out


CAMP = "TimeFantasy_TILES_6.24.17/TILESETS/outside.png"
"""The 1x outside sheet's camp row: the cooking frame and the smoked meat hung on a rod."""
RACK_SIZE = (36, 19)
"""The rack in art pixels: the cooking frame's two A-frames and pole, the smoulder under it."""


def smoke_rack() -> Image.Image:
    """The camp row's cooking frame with its pot taken off (the pot, its hook and the stub above the pole), and a low
    smoulder of damp wood under the pole."""
    img = kit.load(CAMP).crop((22, 269, 22 + RACK_SIZE[0], 269 + RACK_SIZE[1]))
    px = img.load()
    assert px is not None
    for y in range(5, RACK_SIZE[1]):
        for x in range(10, 26):
            px[x, y] = (0, 0, 0, 0)                                                # the pot and its hook
    px[19, 0] = px[20, 0] = px[21, 0] = (0, 0, 0, 0)                               # the hook's stub above the pole
    for y in range(1, 5):
        for x in (19, 20, 21):
            px[x, y] = px[18, y]                                                   # the pole where the hook crossed it
    d = ImageDraw.Draw(img)
    d.line((13, 16, 23, 15), fill=WOOD_DARK)                                       # the smoulder: two damp logs
    d.line((14, 17, 24, 17), fill=WOOD_LINE)
    d.point([(16, 16), (19, 16), (21, 16)], fill=(214, 108, 44, 255))              # coals between them
    d.point((18, 16), fill=(240, 170, 80, 255))
    d.line((12, 18, 25, 18), fill=(36, 36, 42, 120))                               # the shadow on the ash
    return placed(img, RACK)


def meat_on_rack() -> Image.Image:
    """The camp row's two strips of smoked meat, off their rod, hung over the pole between the frames."""
    sheet = kit.load(CAMP)
    strips = [sheet.crop((x, 268, x + 5, 280)) for x in (114, 120)]
    for s in strips:
        px = s.load()
        assert px is not None
        for y in (3, 4):
            px[0, y] = px[4, y] = (0, 0, 0, 0)                                     # the rod either side of the strip
    img, _ = art(*RACK_SIZE)
    for x, s in zip((12, 19), strips):
        img.alpha_composite(s, (x, 0))
    return placed(img, RACK)


def snare(i: int) -> Image.Image:
    """A stake driven in at the edge of a run (Farm and Fort's single sharpened stake, at 2x), a cord from its foot to
    a loop laid open on the ground, in the rope's ramp (lit on its far side, shaded on its near), a short shadow on the
    ash."""
    wire, d = art(15, 14)
    d.line((2, 12, 6, 12), fill=(36, 36, 42, 130))                                 # the stake's shadow
    d.line([(6, 11), (7, 11), (8, 10)], fill=ROPE_LOW)                             # the cord to the loop
    d.ellipse((7, 8, 14, 12), outline=ROPE)                                        # the loop, lying open
    d.arc((7, 8, 14, 12), 200, 320, fill=ROPE_HI)                                  # its far side, catching the light
    d.arc((7, 8, 14, 12), 30, 150, fill=ROPE_LOW)                                  # its near side
    d.line((8, 13, 13, 13), fill=(36, 36, 42, 110))
    sprite = kit.up(wire if i % 2 == 0 else wire.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
    stake = kit.tile(kit.load(kit.FORT), 8.3125, 1.125, 0.25, 0.75)
    put(sprite, stake, 4 if i % 2 == 0 else sprite.width - 12, 0)
    img = canvas()
    put(img, sprite, SNARES[i][0] - 8, SNARES[i][1] - 6)
    return img
