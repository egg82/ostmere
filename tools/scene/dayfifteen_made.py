"""Days fifteen and sixteen's built things, warm because the camp made them: the hall, in four states by its stages, the
hearth at its end, and her beds sown. The hall's walls and roof are Time Fantasy's village longhouse cut down to the
camp's builds' size (the kit's is three times the hut's): its log wall from the doorway to the left end with the right
end's log ends, under its ridge beam, a band of its shingles and its eave, in the made things' warm grade; it stands on
a course of the Ashlands' stones, as the hut does. The hearth shows as Farm and Fort's stone chimney through the hall's
roof at its right end, the beds as Farm and Fort's wheat at three of its growth stages on her turned ground. Nothing is
drawn.
Story spoilers (content/team/week-three.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

import kit
import smoke
from dayone import ghost
from daytwo import footing
from place import canvas, put
from dayfour_made import TURNED
from tints import STONE, WOOD

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
CHIMNEY = ("tf_farmandfort/rpgmaker_VXa/tileB_farmB.png", (128, 131, 160, 171))
"""Farm and Fort's stone chimney stack, its cap and upper courses, cut clear of the plastered wall it is drawn against."""
CHIMNEY_AT = (716, 160)
"""The chimney's bottom-left: through the hall's roof over its right end, its foot among the shingles."""
WHEAT = "curated/buildings/village_crop_wheat.png"
SOWN = [(5, 21, 10, 29), (37, 14, 44, 24), (53, 5, 60, 19)]
"""The wheat strip's growth stages (1x) for the beds' three states, sown, green and ripe: the first shoot, the young
plant's top, the ripe ear and the top of its stalk (the rest stands in the soil, below the mound's crown)."""
MOUNDS_ROW, ROWS = 3, 3
"""Her turned ground: three soil mounds in a row, three rows (dayfour_made.turned's layout)."""


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


def hall_hearth() -> Image.Image:
    """The chimney rising through the hall's roof over its right end, in the world's grey (the stone is not the camp's
    wood, so the layer is not baked)."""
    sheet, box = CHIMNEY
    stack = kit.grade(kit.load(sheet).crop(box), **STONE)
    out = canvas()
    put(out, stack, CHIMNEY_AT[0], CHIMNEY_AT[1] - stack.height)
    return out


def hall_smoke() -> Image.Image:
    """The chimney's smoke: the pack's curls going up from its cap."""
    box = CHIMNEY[1]
    return smoke.plume((CHIMNEY_AT[0] + (box[2] - box[0]) / 2, CHIMNEY_AT[1] - (box[3] - box[1]) - 2), 2)


def beds(state: int) -> Image.Image:
    """Her turned ground sown (`state` 1), green (2) and ripe (3): two plants on the crown of each mound, far rows first."""
    plant = kit.up(kit.load(WHEAT).crop(SOWN[state - 1]))
    out = canvas()
    for row in range(1, ROWS + 1):
        for i in range(MOUNDS_ROW):
            x, y = TURNED[0] + i * 21 + (row % 2) * 6, TURNED[1] + (row - 1) * 11
            for dx in (4, 12):
                put(out, plant, x + dx, y + 12 - plant.height)
    return out
