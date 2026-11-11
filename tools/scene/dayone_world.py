"""Day one's found world, cool and drawn in its final colours: the shape on the ridge, the fog in the valley and the
stream's steam rising out of it (all behind the ruin's walls), the player's smoke rising before them, and the prints in the ash.

Soft things are drawn at the art's 1x grain, blurred, then snapped to a few alpha levels and scaled with NEAREST, so
even fog steps in the art's pixels.
Story spoilers (content/team/day-one.md, Art): never shown to the owner.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import kit
from dayone import LARDER, RACK, RACK_SIZE
from kit import T
from place import H, RIDGE, W

FOG = (176, 184, 194)
PRINTS = [(9.4 * T, 4.45 * T), (8.9 * T, 4.62 * T), (7.45 * T, 4.62 * T), (7.2 * T, 5.65 * T), (6.6 * T, 5.95 * T),
          (LARDER[0] + 1.75 * T, LARDER[1] + 0.75 * T)]
"""The prints' waypoints, routed along the wall's foot and between the fireback and the damp heap so neither covers
them."""


def blank_mask() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    m = Image.new("L", (W // 2, H // 2))
    return m, ImageDraw.Draw(m)


def soft(mask: Image.Image, blur: float, levels: tuple[int, ...], colour: tuple[int, int, int]) -> Image.Image:
    """A half-size mask blurred, snapped to a few alpha levels of one colour, scaled up."""
    a = mask.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", mask.size, (*colour, 255))
    out.putalpha(Image.eval(a, lambda v: max((lv for lv in levels if v >= lv), default=0)))
    return kit.up(out)


def behind(img: Image.Image, walls: Image.Image) -> Image.Image:
    """The layer cut away wherever the ruin's walls and roof stand, so it reads as beyond them."""
    out = img.copy()
    out.putalpha(ImageChops.subtract(img.getchannel("A"), walls))
    return out


def ridge_shape(walls: Image.Image, square: bool = True) -> Image.Image:
    """On the far ridge, where the light was, something dark and square, faint in the haze. `square=False` is the
    ridge's second state: the same line with nothing on it."""
    m, d = blank_mask()
    cx, cy = int(RIDGE[0] / 2), int(RIDGE[1] / 2)
    if square:
        d.rectangle((cx - 5, cy - 3, cx + 5, cy + 2), fill=255)
        d.rectangle((cx - 4, cy - 5, cx + 3, cy - 3), fill=255)
        d.point([(cx - 3, cy + 3), (cx + 3, cy + 3)], fill=255)
    d.line((cx - 27, cy + 4, cx + 30, cy + 4), fill=130)                          # the ridge's line, fainter
    return behind(soft(m, 0.6, (60, 110, 150), (64, 68, 82)), walls)


FOG_BANDS = [(-20, 28, 120, 40), (90, 34, 250, 48), (156, 46, 260, 62), (-10, 48, 80, 58)]
"""The fog's long bands, ellipses at the art's 1x grain, the third clear of the track; each lies on the low ground
along its lowest edge, which is its depth (fog_ground)."""
STEAM = [(190, 50), (226, 60), (104, 40)]
"""Where the stream steams, (x, ground row) at 1x: behind the wall stub, right of it and behind the long wall, none in
the gap, where the track and its cairns are."""


def fog_ground(band: tuple[int, int, int, int]) -> int:
    """The scene row a fog band lies along: its depth."""
    return band[3] * 2


def steam_ground(spot: tuple[int, int]) -> int:
    """The scene row a column of steam rises from: its depth."""
    return spot[1] * 2 + 5


def valley_fog(walls: Image.Image) -> list[Image.Image]:
    """Fog lying in the low ground past the walls, in long bands, one image per band so each sorts at its own depth.
    The bands are blurred as one; each pixel goes to the band whose own shape is strongest there (the nearer on a tie),
    so where two meet their haze does not stack."""
    m, d = blank_mask()
    own: list[Image.Image] = []
    for band in FOG_BANDS:
        d.ellipse(band, fill=255)
        alone, ad = blank_mask()
        ad.ellipse(band, fill=255)
        own.append(alone.filter(ImageFilter.GaussianBlur(3)))
    whole = behind(soft(m, 3, (28, 50, 72), FOG), walls)
    out: list[Image.Image] = []
    for k, mine in enumerate(own):
        keep = Image.new("L", m.size, 255)
        for j, other in enumerate(own):
            if j == k:
                continue
            if FOG_BANDS[j][3] > FOG_BANDS[k][3]:          # the nearer band wins a tie: k must be strictly stronger
                wins = kit.point(ImageChops.subtract(mine, other), lambda v: 255 if v > 0 else 0)
            else:
                wins = kit.point(ImageChops.subtract(other, mine), lambda v: 255 if v == 0 else 0)
            keep = ImageChops.multiply(keep, wins)
        band = whole.copy()
        band.putalpha(ImageChops.multiply(whole.getchannel("A"), kit.up(keep)))
        out.append(band)
    return out


def stream_steam(walls: Image.Image) -> list[Image.Image]:
    """The warm stream's steam rising out of the fog: at a few spots a thin wisp of slow puffs, each higher one
    smaller, fainter and drifted a little (narrower than a figure, so it never reads as one), apart from the player's smoke, which stands straight and unbroken. One
    image per column, so each sorts at the depth it rises from."""
    rng = random.Random(5)
    out: list[Image.Image] = []
    for cx, base in STEAM:
        m, d = blank_mask()
        x = float(cx)
        for k in range(6):
            r = 1.8 - k * 0.15
            y = base - k * 4
            x += rng.uniform(-0.9, 0.9)
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=210 - k * 28)
        out.append(behind(soft(m, 0.8, (40, 80, 120), FOG), walls))
    return out


def smoke_plume(near_walls: Image.Image) -> Image.Image:
    """The player's smoke, standing up from the rack's pole in the still air: a column of overlapping billows, lumpy
    and broken at the edges, that leans a pixel or two as it climbs, widens and thins until it is gone. Warm pale
    grey, apart from the cool fog and the wandering steam. It rises in front of the ruin, so where `near_walls` stand
    behind it the wall shows through it."""
    m, d = blank_mask()
    core, _ = blank_mask()
    cd, rng = ImageDraw.Draw(core), random.Random(9)
    base, top, cx = int(RACK[1] / 2) + 6, 18, int(RACK[0] / 2) + RACK_SIZE[0] // 2
    n = 40
    for k in range(n, -1, -1):
        t = k / n                                                                   # 0 at the pole, 1 at the top
        y = base - t * (base - top)
        x = cx + 2.0 * math.sin(t * 4.2 + 0.6) + rng.uniform(-0.8, 0.8) * (0.4 + t)
        r = 3.0 + t * 8.5
        fade = 255 - round(200 * t ** 1.1)
        for _ in range(3):                                                          # lobes: a billow, not a bead
            lx, ly = x + rng.uniform(-0.7, 0.7) * r, y + rng.uniform(-0.5, 0.5) * r
            lr = r * rng.uniform(0.45, 0.8)
            d.ellipse((lx - lr, ly - lr * 0.8, lx + lr, ly + lr * 0.8), fill=fade)
        if k % 3 == 0 and t < 0.75:                                                 # a lit face on some billows
            lx = x + rng.uniform(-0.45, 0.45) * r
            cd.ellipse((lx - r * 0.35, y - r * 0.3, lx + r * 0.35, y + r * 0.3), fill=fade)
    for _ in range(110):                                                            # bites out of the edge
        t = rng.random()
        y, x = base - t * (base - top), cx + rng.uniform(-1, 1) * (4 + t * 10)
        d.ellipse((x - 1.5, y - 1.2, x + 1.5, y + 1.2), fill=0)
    body = soft(m, 0.7, (40, 85, 135, 180), (156, 152, 150))
    lit = soft(core, 0.8, (110, 175), (208, 202, 194))
    out = Image.alpha_composite(body, lit)
    veiled = kit.point(out.getchannel("A"), lambda v: v * 0.4)
    out.putalpha(Image.composite(veiled, out.getchannel("A"), near_walls))
    return out


def prints(path: list[tuple[float, float]], step: float = 9.0) -> Image.Image:
    """One set of prints in the ash along `path` (scene pixels): a dark print every `step`, left and right of the line
    in turn."""
    img = Image.new("RGBA", (W // 2, H // 2))
    d = ImageDraw.Draw(img)
    side, carry = 1, 0.0
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / length, (x1 - x0) / length                            # the normal, for left and right
        at = carry
        while at < length:
            t = at / length
            x, y = (x0 + (x1 - x0) * t + nx * 1.5 * side) / 2, (y0 + (y1 - y0) * t + ny * 1.5 * side) / 2
            d.rectangle((int(x), int(y), int(x) + 1, int(y)), fill=(40, 42, 50, 220))
            side, at = -side, at + step
        carry = at - length
    return kit.up(img)
