"""Day eleven's built things, warm because the camp made them: the family's hut and the board by the fire with its one
mark. The hut's walls are Farm and Fort's low pointed logs on a course of the Ashlands' stones, its roof brush drawn
as the woodshed's is (the kit's huts are four and five tiles wide, three times the camp's builds); the board is Time
Fantasy's wooden signboard, its carving planed off. What is drawn is the roof, the doorway's dark and the one mark.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations


from PIL import Image

import kit
from daytwo import cut, footing
from dayone_poses import outlined
from dayone import SHADOW, gable, ghost
from kit import FORT
from place import canvas, put
from tints import WOOD

HUT = (428, 167)
"""The hut's bottom-left: inside the ring's last stretch, against the palisade, above the stakes' stack."""
HUT_W = 48
LOW = (144, 96, 176, 128)
"""Farm and Fort's low stretch of pointed logs (the palisade's gate leaf is cut from it): the hut's walls."""
WALL_H = 24
STONES_H = 16
"""The stone course's height (the footing's), which the walls sit half into."""
DOOR = (18, 18)
"""The doorway in the wall: its left x from the wall's left, and its height."""
BOARD = "TimeFantasy_TILES_6.24.17/TILESETS/desert.png"
SIGN = (16, 16, 32, 32)
"""The desert sheet's wooden signboard on its post (1x): a face of three planks, the middle one carved."""
CARVED, PLAIN = (4, 5, 6), 3
"""The face's grained and carved middle rows, and the plain row each is planed to."""
CUT = (108, 60, 74, 255)
"""The carving's own dark, for the mark."""
BOARD_AT = (334, 212)
"""The board's post foot: by the fire, behind the stool, on the bare ground between the watch fire and the woodshed."""


def _walls() -> Image.Image:
    leaf = kit.load(FORT).crop(LOW)
    wall = Image.new("RGBA", (HUT_W, WALL_H))
    for x in range(0, HUT_W, leaf.width):
        wall.alpha_composite(leaf.crop((0, leaf.height - WALL_H, leaf.width, leaf.height)), (x, 0))
    wall = wall.crop((0, 0, HUT_W, WALL_H))
    d = Image.new("RGBA", (DOOR[0] + 12, WALL_H))
    door = Image.new("RGBA", (12, DOOR[1]), SHADOW)
    d.alpha_composite(door, (DOOR[0], WALL_H - DOOR[1]))
    wall.alpha_composite(d)
    return wall


def _roof() -> Image.Image:
    """Thatch over the walls, eaves past them each side, as the woodshed's roof."""
    return kit.up(gable(HUT_W // 2 + 6, 14, 111))


def _timber() -> Image.Image:
    """The hut's wood: the log walls with the doorway and the brush roof over them, in the made things' warm grade."""
    x0, base = HUT
    walls, roof = kit.grade(_walls(), **WOOD), kit.grade(_roof(), **WOOD)
    out = canvas()
    put(out, walls, x0, base - STONES_H // 2 - WALL_H)
    put(out, roof, x0 + (HUT_W - roof.width) / 2, base - STONES_H // 2 - WALL_H - roof.height + 6)
    return out


def _stones() -> Image.Image:
    """The course of stones it stands on, the world's cool grey."""
    x0, base = HUT
    stones = footing(HUT_W)
    out = canvas()
    put(out, stones, x0 - (stones.width - HUT_W) / 2, base - stones.height)
    return out


def hut(building: bool = False) -> Image.Image:
    """The hut built; or `building`, its stones laid and the rest a ghost where it will stand. The stones keep the world's
    cool grey and only the wood takes the warm grade, as the woodstack's, so the layer is not baked."""
    out = ghost(_timber()) if building else _timber()
    out.alpha_composite(_stones())
    return out


def tally_board() -> Image.Image:
    """The signboard with its face planed smooth, and one mark cut in it."""
    sign = cut(BOARD, SIGN)
    for row in CARVED:
        sign.paste(sign.crop((0, PLAIN, sign.width, PLAIN + 1)), (0, row))
    px = sign.load()
    assert px is not None
    for y in range(3, 8):
        px[sign.width // 2, y] = CUT
    board = outlined(kit.up(sign))
    out = canvas()
    put(out, board, BOARD_AT[0] - board.width / 2, BOARD_AT[1] - board.height)
    return out
