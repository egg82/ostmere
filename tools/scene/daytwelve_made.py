"""Day twelve's built things: the cellar's mouth in four states at the ruin's north wall, the lamps on the gate's posts
and the burning at the scrub's edge. Pieces are Time Fantasy's: the spoil is Farm and Fort's soil mounds, the shovel its
tool row's, the steps the Caves and Mines stair cut down inside its stone entrance, the doorway's timbers the ruined
house sheet's boarded doorway, the lamps the mine sheet's hanging lanterns, the pyre the outside sheet's cut logs under
the torch sheet's flames. Drawn are the pit's dark, which no sheet has at this size, and the pyre's smoke.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

import random

from PIL import Image, ImageChops, ImageDraw

import kit
from daythree_poses import shovel
from dayone_world import blank_mask, soft
from dayfour_made import FARM, MOUNDS
from daytwo import cut
from place import H, W, canvas, put
from tints import SOIL, STONE, WOOD

CELLAR = (74, 147)
"""The cellar's mouth: its centre at the ruin's north wall, where the wall's foot meets the camp's floor."""
PIT = (18, 11)
"""The pit at the art's 1x grain: its width, and how far it reaches out from the wall's foot when dug through."""
CAVE = "cavesandmines_TFcolor_update_8.24/_tfrecolor_8.24/1X/tilesets/tileB_cave1.png"
STEPS = (142, 179, 160, 192)
"""The stair inside the cave sheet's stone entrance (1x): treads going down into its dark."""
RUINED = "TimeFantasy_TILES_6.24.17/RPGMAKER/RMVX/tileC_HOUSE_ruined.png"
HEAD, LEFT, RIGHT, BOARD = (377, 33, 455, 42), (376, 42, 382, 93), (448, 42, 455, 93), (418, 44, 448, 74)
"""The boarded doorway's head timber, its two posts, and one of the boards nailed across it."""
DOOR_H = 22
"""How much of the posts stands above the stair."""
SPOIL_AT = (CELLAR[0] + 20, CELLAR[1] + 24)
"""The spoil's heap: its bottom-left, right of the pit and out from the wall."""
LANTERNS = "cavesandmines_TFcolor_update_8.24/_tfrecolor_8.24/1X/tilesets/tileB_cave2.png"
UNLIT, LIT = (116, 52, 123, 59), (116, 68, 123, 75)
"""The mine sheet's small hanging lantern (1x), dark and burning."""
IRON = kit.Grade(sat=0.15, mul=(1.0, 1.0, 1.0), bright=0.85, contrast=1.1)
"""The lanterns' teal metal taken to iron."""
POSTS = (270, 312)
"""Where each lamp hangs: off the gate's left post's outer face and the right post's."""
LAMP_Y = 110
OUTSIDE = "TimeFantasy_TILES_6.24.17/TILESETS/outside.png"
LOGS = (144, 52, 157, 62)
"""The outside sheet's pile of cut logs (1x)."""
TORCH = "TimeFantasy_TILES_6.24.17/TILESETS/animated/torch.png"
FLAME = (4, 1, 13, 15)
"""The torch sheet's loose flame (1x)."""
PYRE = (452, 238)
"""The pyre's foot: at the scrub's edge on the scene's right, past the stump and the snares' run."""
SEED = 112
PIT_DARK, LIP, DOOR_DARK = (30, 26, 26, 255), (84, 74, 66, 255), (24, 22, 24, 255)

def _pit(depth: int) -> Image.Image:
    """The dug ground at the wall's foot, `depth` 1 (a scrape) or 2 (the pit). Drawn at the 1x grain, its edge
    ragged, the near lip lit."""
    w, reach = PIT[0] - (6 if depth == 1 else 0), PIT[1] * depth // 2
    small = Image.new("RGBA", (W // 2, H // 2))
    d = ImageDraw.Draw(small)
    x0, y0 = CELLAR[0] // 2 - w // 2, CELLAR[1] // 2
    r = random.Random(SEED + depth)
    for x in range(x0, x0 + w):
        bottom = y0 + reach - (1 if x in (x0, x0 + w - 1) else r.randrange(2))
        d.line((x, y0, x, bottom), fill=PIT_DARK)
        d.point((x, bottom + 1), fill=LIP)
    return kit.up(small)


def _spoil(n: int) -> Image.Image:
    """`n` of the soil mounds heaped beside the pit, the dark soil from under the ash."""
    out = canvas()
    for i, box in enumerate(MOUNDS[:n]):
        m = kit.grade(cut(FARM, box), **SOIL)
        put(out, m, SPOIL_AT[0] + (i % 2) * 12 - (i // 2) * 6, SPOIL_AT[1] - m.height - (i // 2) * 8)
    return out


def _tool() -> Image.Image:
    """The shovel stuck upright in the spoil, its blade in the heap."""
    out = canvas()
    s = kit.grade(shovel(), **WOOD)
    put(out, s, SPOIL_AT[0] + 4, SPOIL_AT[1] - s.height - 8)
    return out


def _steps() -> Image.Image:
    """The cut stair filling the pit, its treads stepping down toward the wall."""
    stair = kit.grade(kit.up(kit.load(CAVE).crop(STEPS)), **STONE)
    out = canvas()
    put(out, stair, CELLAR[0] - stair.width / 2, CELLAR[1])
    return out


def _frame() -> Image.Image:
    """The doorway's timbers set at the stair's head, against the wall: two posts and the head timber across them,
    the way in dark between them; one board pulled off and left leaning beside it."""
    sheet = kit.load(RUINED)
    head, left, right, board = (kit.grade(sheet.crop(b), **WOOD) for b in (HEAD, LEFT, RIGHT, BOARD))
    span = PIT[0] * 2 + 4
    head = _ends(head, span)
    x0, top = CELLAR[0] - span / 2, CELLAR[1] - DOOR_H
    out = canvas()
    ImageDraw.Draw(out).rectangle((x0 + left.width, top, x0 + span - right.width - 1, CELLAR[1]), fill=DOOR_DARK)
    put(out, left.crop((0, 0, left.width, DOOR_H)), x0, top)
    put(out, right.crop((0, 0, right.width, DOOR_H)), x0 + span - right.width, top)
    put(out, head, x0, top - head.height + 2)
    put(out, board, x0 - board.width + 4, CELLAR[1] - board.height + 4)
    return out


def _ends(head: Image.Image, span: int) -> Image.Image:
    """The head timber cut to `span`: its left end and its right end, the middle dropped."""
    out = Image.new("RGBA", (span, head.height))
    out.alpha_composite(head.crop((0, 0, span // 2, head.height)))
    out.alpha_composite(head.crop((head.width - span + span // 2, 0, head.width, head.height)), (span // 2, 0))
    return out


def cellar(stage: int) -> Image.Image:
    """The mouth after dig stage `stage`: 1 the ground broken and the spoil heaped, 2 the pit, 3 the stair found in
    it, 4 the doorway's timbers set at its head and the shovel put away."""
    out = _pit(min(stage, 3)) if stage < 3 else _steps()
    out.alpha_composite(_tool() if stage < 4 else _frame())
    out.alpha_composite(_spoil(min(stage + 1, 3)))
    return out


def _lantern(box: tuple[int, int, int, int]) -> Image.Image:
    return kit.up(kit.grade(kit.load(LANTERNS).crop(box), **IRON))


def lamp(n: int, lit: bool = False) -> Image.Image:
    """Lamp `n` (0 the left post, 1 the right) on a short peg off its post."""
    sprite = _lantern(LIT if lit else UNLIT)
    out = canvas()
    x = POSTS[n] - (sprite.width if n == 0 else 0)
    put(out, sprite, x, LAMP_Y)
    ImageDraw.Draw(out).line((POSTS[n] - (4 if n == 0 else 0), LAMP_Y, POSTS[n] + (0 if n == 0 else 4), LAMP_Y),
                             fill=(40, 34, 30, 255), width=2)
    return out


def lamps_lit() -> Image.Image:
    out = lamp(0, lit=True)
    out.alpha_composite(lamp(1, lit=True))
    return out


def lamp_light() -> Image.Image:
    """A small warm light round each lamp, for a screen blend."""
    left, right = (kit.radial((W, H), (POSTS[n] + (-7 if n == 0 else 7), LAMP_Y + 8), 22, 140, 0) for n in (0, 1))
    out = Image.new("RGBA", (W, H), (150, 82, 30, 255))
    out.putalpha(ImageChops.lighter(left, right))
    return out


def _stack() -> Image.Image:
    """The log piles stacked three rows high, narrowing to the top."""
    logs = kit.grade(kit.up(kit.load(OUTSIDE).crop(LOGS)), **WOOD)
    step = logs.height - 6
    out = Image.new("RGBA", (logs.width * 3, logs.height + 2 * step))
    for row, xs in enumerate(((0, 1, 2), (0.5, 1.5), (1,))):
        for x in xs:
            out.alpha_composite(logs, (round(x * (logs.width - 2)), (2 - row) * step))
    return out


def _top() -> float:
    """Where the flames stand: the stack's top."""
    return PYRE[1] - _stack().height + 6


def pyre() -> Image.Image:
    """The logs stacked at the scrub's edge, and their smoke going up, leaning with the wind (drawn, as the road's
    smoke is: the kit's wisps are a candle's)."""
    wood = _stack()
    m, d = blank_mask()
    r = random.Random(SEED)
    x = PYRE[0] / 2
    for k in range(16):
        y = _top() / 2 - 4 - k * 3
        rr = 2.5 + k * 0.5
        x -= r.uniform(0.2, 1.0)
        d.ellipse((x - rr, y - rr * 0.8, x + rr, y + rr * 0.8), fill=250 - k * 12)
    out = soft(m, 0.8, (90, 150, 200), (172, 166, 158))
    put(out, wood, PYRE[0] - wood.width / 2, PYRE[1] - wood.height)
    return out


def pyre_flames() -> Image.Image:
    """The torch sheet's flames along the stack's top."""
    flame = kit.up(kit.load(TORCH).crop(FLAME))
    out = canvas()
    for k, dx in enumerate((-16, 0, 14)):
        put(out, flame, PYRE[0] + dx - flame.width / 2, _top() - flame.height + 4 + (k % 2) * 4)
    return out
