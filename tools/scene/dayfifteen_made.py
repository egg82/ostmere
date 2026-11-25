"""Day fifteen's built thing, warm because the camp made it: the hall, in four states by its stages. Its walls and roof
are Time Fantasy's village longhouse cut down to the camp's builds' size (the kit's is three times the hut's): its log
wall from the doorway to the left end with the right end's log ends, under its ridge beam, a band of its shingles and
its eave, in the made things' warm grade; it stands on a course of the Ashlands' stones, as the hut does. Nothing is
drawn. Story spoilers (content/team/week-three.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

import kit
from dayone import ghost
from daytwo import footing
from place import canvas, put
from tints import WOOD

LONGHOUSE = "village_longhouse"
"""The curated longhouse (1x, 144x90): rows 8-15 its ridge beam, 16-56 shingles, 57-60 the eave, 61-88 the log wall."""
BEAM, SHINGLES, EAVE = (8, 16), (49, 57), (57, 61)
"""The roof's bands kept (1x rows, end exclusive): the ridge beam, the shingles' lowest courses, the eave."""
WALL = (70, 89)
"""The log wall's lower courses (1x rows): the doorway's foot to the logs' ends; the eave hides where it is cut."""
LEFT, RIGHT = (0, 52), (132, 144)
"""The columns kept (1x): the left end through the doorway, and the right end's log ends."""
HALL = (632, 222)
"""The hall's bottom-left: the open ground right of the gap fire, against the palisade."""
STONES_H = 16
"""The stone course's height (the footing's), which the walls sit half into."""
RISEN = 7
"""The wall's courses (1x rows, from its foot) stood at stage 2: the first logs on the stones."""


def _band(top: int, bottom: int) -> Image.Image:
    """Rows top..bottom of the longhouse, its left end and right end joined, at the scene's 2x."""
    house = kit.load(f"curated/buildings/{LONGHOUSE}.png")
    left, right = house.crop((LEFT[0], top, LEFT[1], bottom)), house.crop((RIGHT[0], top, RIGHT[1], bottom))
    band = Image.new("RGBA", (left.width + right.width, bottom - top))
    band.alpha_composite(left)
    band.alpha_composite(right, (left.width, 0))
    return kit.up(band)


def _roof(half: bool) -> Image.Image:
    """The ridge beam, the shingles and the eave stacked; `half`, only the left half is on."""
    bands = [_band(*BEAM), _band(*SHINGLES), _band(*EAVE)]
    roof = Image.new("RGBA", (bands[0].width, sum(b.height for b in bands)))
    y = 0
    for b in bands:
        roof.alpha_composite(b, (0, y))
        y += b.height
    return roof.crop((0, 0, roof.width // 2, roof.height)) if half else roof


def _timber(stage: int) -> Image.Image:
    """The hall's wood at `stage` (1 to 4, the states at its stages 2, 4, 6 and 8), in the made things' warm grade."""
    x0, base = HALL
    wall = _band(*WALL)
    top = base - STONES_H // 2 - wall.height
    if stage == 1:
        wall = wall.crop((0, wall.height - RISEN * 2, wall.width, wall.height))
    out = canvas()
    put(out, kit.grade(wall, **WOOD), x0, base - STONES_H // 2 - wall.height)
    if stage >= 3:
        roof = kit.grade(_roof(half=stage == 3), **WOOD)
        put(out, roof, x0, top - roof.height + 2)
    return out


def _stones() -> Image.Image:
    """The course of stones it stands on, the world's cool grey."""
    x0, base = HALL
    width = _band(*WALL).width
    stones = footing(width)
    out = canvas()
    put(out, stones, x0 - (stones.width - width) / 2, base - stones.height)
    return out


def hall(stage: int) -> Image.Image:
    """The hall at `stage` (1 to 4); 0 is the whole hall as a ghost on its stones, where it will stand while it is
    being built. The stones keep the world's cool grey and only the wood takes the warm grade, so the layer is not
    baked."""
    out = ghost(_timber(4)) if stage == 0 else _timber(stage)
    out.alpha_composite(_stones())
    return out
