"""Time Fantasy kit helpers for the scene generator: load a sheet, crop tiles, upscale, grime a character, grade.

Moved from docs/research/look-test/compose.py (the approved night camp), typed and split into small functions.
"""
from __future__ import annotations

import os
import random
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TypedDict

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

TF = Path(os.environ.get("TIME_FANTASY", os.path.expanduser("~/src/time-fantasy")))
T = 32
"""Tile size on the 2x (RPG Maker VX) sheets, which is the scene's working scale."""
ASH_B = "tf_ashlands/2x_RMVX/tf_B_ashlands_2.png"
FORT = "tf_farmandfort/rpgmaker_VXa/tileB_fortA.png"


def load(rel: str) -> Image.Image:
    return Image.open(TF / rel).convert("RGBA")


def tile(sheet: Image.Image, c: float, r: float, w: float = 1, h: float = 1) -> Image.Image:
    """Tiles (c, r) to (c + w, r + h); fractions crop part of a tile."""
    return sheet.crop((int(c * T), int(r * T), int((c + w) * T), int((r + h) * T)))


def resize(img: Image.Image, size: tuple[int, int], resample: Image.Resampling = Image.Resampling.NEAREST) -> Image.Image:
    """Resize, nearest-neighbour unless told otherwise. Pillow's stub types `size` with a numpy alias, which is unknown
    here (no numpy), so this is the one place that call is not checked."""
    return img.resize(size, resample)  # pyright: ignore[reportUnknownMemberType] -- Pillow stub types it with a numpy alias


def point(img: Image.Image, fn: Callable[[int], float]) -> Image.Image:
    """Map every sample through fn. Pillow's stub types the callable's argument as an expression-builder and the lut
    with a numpy alias, so this is the one place that call is not checked."""
    return img.point(fn)  # pyright: ignore[reportUnknownMemberType] -- Pillow stub types it with a numpy alias


class Pixels(Protocol):
    """What `Image.load()` returns, as far as reading goes."""
    def __getitem__(self, xy: tuple[int, int], /) -> float | tuple[int, ...]: ...


def rgba(px: Pixels, x: int, y: int) -> tuple[int, int, int, int]:
    """The RGBA pixel at (x, y); Pillow types an access as returning a float for single-band images too."""
    v = px[x, y]
    assert isinstance(v, tuple) and len(v) == 4
    return v


def pixels(rows: list[str], key: dict[str, tuple[int, int, int, int]]) -> Image.Image:
    """A 1x sprite from rows of key characters ('.' is clear)."""
    img = Image.new("RGBA", (max(len(r) for r in rows), len(rows)))
    px = img.load()
    assert px is not None
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = key[ch]
    return img


def up(img: Image.Image) -> Image.Image:
    return resize(img, (img.width * 2, img.height * 2))


class Grade(TypedDict):
    """The keyword arguments of `grade`."""
    sat: float
    mul: tuple[float, float, float]
    bright: float
    contrast: float


def curated(name: str) -> Image.Image:
    """The curated props are 1x; the scene works at 2x."""
    return up(load(f"curated/buildings/{name}.png"))


def battler(char: str, frame: str) -> Image.Image:
    """A side-view battler frame (1x, 48 px), upscaled; char like "2_3" is set 2, character 3."""
    s, n = char.split("_")
    return up(load(f"tf_svbattle/singleframes/set{s}/{n}/{char}_{frame}.png"))


SHEET_FACING = {"down": 0, "left": 1, "right": 2, "up": 3}
"""The rows of a walking-character sheet."""


def walker(rel: str, who: int, facing: str, col: int = 1, drop: int = 0) -> Image.Image:
    """One frame of a walking-character sheet (eight characters in a 4x2 block, each 3 columns x 4 facings of 26x36),
    upscaled. `drop` rows are cut off the bottom and the rest moved down by as many, so the feet stay put: the kit has
    no sitting frames, and a standing frame cut short sits."""
    x, y = (who % 4) * 78 + col * 26, (who // 4) * 144 + SHEET_FACING[facing] * 36
    frame = load(rel).crop((x, y, x + 26, y + 36 - drop))
    out = Image.new("RGBA", (26, 36))
    out.alpha_composite(frame, (0, drop))
    return up(out)


def keep_alpha(img: Image.Image, rgb: Image.Image) -> Image.Image:
    out = rgb.convert("RGBA")
    out.putalpha(img.getchannel("A"))
    return out


def tint(rgb: Image.Image, mul: tuple[float, float, float]) -> Image.Image:
    r, g, b = rgb.split()
    return Image.merge("RGB", (point(r, lambda v: v * mul[0]), point(g, lambda v: v * mul[1]),
                               point(b, lambda v: v * mul[2])))


def grime(img: Image.Image) -> Image.Image:
    """Drained, darker, a little browner: worn clothes, no bright dyes (compose.py's GRIME, unchanged)."""
    rgb = ImageEnhance.Color(img.convert("RGB")).enhance(0.35)
    rgb = ImageEnhance.Brightness(rgb).enhance(0.78)
    return keep_alpha(img, tint(rgb, (1.06, 1.0, 0.88)))


def grade(img: Image.Image, sat: float, mul: tuple[float, float, float], bright: float, contrast: float) -> Image.Image:
    """compose.py's grade, alpha kept, so every layer is graded the same way before it is cut out."""
    rgb = ImageEnhance.Color(img.convert("RGB")).enhance(sat)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    return keep_alpha(img, tint(rgb, mul))


def calm(img: Image.Image, k: float) -> Image.Image:
    """Pull the pixels toward their blurred neighbourhood by k (0-1): the same ground with less noise."""
    soft = img.filter(ImageFilter.GaussianBlur(6))
    return keep_alpha(img, Image.blend(img.convert("RGB"), soft.convert("RGB"), k))


def radial(size: tuple[int, int], centre: tuple[float, float], radius: float, inner: int, outer: int,
           squash: float = 1.0) -> Image.Image:
    """Mask: `inner` at the centre falling to `outer` at radius (0-255); squash < 1 flattens it into an ellipse."""
    m = Image.new("L", size, outer)
    d = ImageDraw.Draw(m)
    steps = 40
    for i in range(steps, 0, -1):
        f = i / steps
        rr = radius * f
        d.ellipse((centre[0] - rr, centre[1] - rr * squash, centre[0] + rr, centre[1] + rr * squash),
                  fill=int(inner + (outer - inner) * f))
    return m.filter(ImageFilter.GaussianBlur(radius / 10))


def ash(size: tuple[int, int], n: int, colour: tuple[int, int, int], seed: int) -> Image.Image:
    """Ash hanging in the air: single specks, some two wide, some faint."""
    img = Image.new("RGBA", size)
    d = ImageDraw.Draw(img)
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.randrange(size[0]), r.randrange(size[1])
        a = r.choice((90, 140, 200))
        d.point((x, y), fill=(*colour, a))
        if r.random() < .3:
            d.point((x + 1, y), fill=(*colour, a))
    return img
