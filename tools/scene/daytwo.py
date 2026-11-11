"""Day two's made things, warm because the camp made them: her shelter and the woodstack, put together from Farm and
Fort and Time Fantasy pieces at the scene's 2x, and her bedroll for the nights she sleeps in the open.
Story spoilers (content/team/day-two.md, Art): never shown to the owner.
"""
from __future__ import annotations

from PIL import Image

import kit
from kit import ASH_B, FORT, T
from place import canvas, put
from tints import ACCENT, WOOD

TENT = "tf_farmandfort/rpgmaker_VXa/tileB_tent.png"
OUTSIDE = "TimeFantasy_TILES_6.24.17/RPGMAKER/RMVX/tileB_outside.png"
SHELTER = (2.4 * T, 6.25 * T)
"""Her shelter's top-left: beside the lean-to on its open side, its foot on the lean-to's ground line, short of the
smoke rack."""
WOODSTACK = (10.35 * T, 3.55 * T)
"""The woodstack's top-left: at the foot of the wall stub past the gap, behind the carried-in stones."""


def cut(sheet: str, box: tuple[int, int, int, int]) -> Image.Image:
    """A piece cut from a sheet by its pixel box and trimmed to its drawn pixels."""
    piece = kit.load(sheet).crop(box)
    bbox = piece.getchannel("A").getbbox()
    assert bbox is not None, f"nothing drawn in {sheet} {box}"
    return piece.crop(bbox)


def bedroll() -> Image.Image:
    """The Farm and Fort tent sheet's plain brown bedroll, laid lengthwise across the view (pillow end left)."""
    return cut(TENT, (0, 416, 32, 480)).transpose(Image.Transpose.ROTATE_90)


def hide_frame() -> Image.Image:
    """Farm and Fort's hide stretched on a pole frame: two posts, a cross pole, the hide lashed between them."""
    return cut(FORT, (192, 448, 256, 512))


def n1_shelter() -> Image.Image:
    """A hide hung on a pole frame for a windbreak, low and small, her bedroll laid under it, its ends showing."""
    img = canvas()
    frame, roll = hide_frame(), bedroll()
    put(img, roll, SHELTER[0] + (frame.width - roll.width) / 2, SHELTER[1] + frame.height - roll.height + 2)
    put(img, frame, SHELTER[0], SHELTER[1])
    return img


def _firewood() -> list[Image.Image]:
    """Time Fantasy's two split-firewood stacks (the outside sheet's pyramid and its low pair)."""
    return [cut(OUTSIDE, (224, 193, 254, 223)), cut(OUTSIDE, (224, 229, 254, 256))]


def footing(width: int) -> Image.Image:
    """A course of the Ashlands' loose stones laid in a row, the found world's cool grey (the stones carried in)."""
    stones = [kit.tile(kit.load(ASH_B), c, 2) for c in (0, 3, 0, 3, 0)]
    stones = [s.crop(s.getchannel("A").getbbox()) for s in stones]
    row = Image.new("RGBA", (width + 16, max(s.height for s in stones)))
    x = 0
    for s in stones:
        if x >= row.width:
            break
        row.alpha_composite(s, (x, row.height - s.height))
        x += s.width - 3
    return kit.grade(row.crop(row.getchannel("A").getbbox()), **ACCENT)


def woodstack() -> Image.Image:
    """Split firewood stacked three wide on a stone footing against the wall stub. The stones keep the world's cool
    grey and only the wood takes the made things' warm grade, so the layer is not baked."""
    pyramid, pair = _firewood()
    wood = Image.new("RGBA", (pyramid.width * 2 + pair.width, pyramid.height))
    wood.alpha_composite(pyramid, (0, 0))
    wood.alpha_composite(pair, (pyramid.width - 2, wood.height - pair.height))
    wood.alpha_composite(pyramid, (pyramid.width + pair.width - 4, 0))
    wood = kit.grade(wood.crop(wood.getchannel("A").getbbox()), **WOOD)
    stones = footing(wood.width)
    img = canvas()
    x0, base = WOODSTACK[0], WOODSTACK[1] + wood.height
    put(img, stones, x0 - (stones.width - wood.width) / 2, base - stones.height / 2)
    put(img, wood, x0, base - stones.height / 2 - wood.height + 3)
    return img
