"""Days four to seven's found world, cool and drawn in its final colours: the fog over the whole scene and the haze it
thins to, the kill and prints at the track's far end, the ring of prints at the scrub's edge, the grey shapes on the ridge,
the eyes at the edge of the firelight, and the steam off the damp wood under the player's hand.
Soft things are drawn at the art's 1x grain, blurred and snapped to a few alpha levels, as day one's fog is.
Story spoilers (content/team/days-four-to-seven.md, Art): never shown to the owner."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import kit
from daytwo import cut
from dayone_world import FOG, behind, blank_mask, prints, soft
from kit import T
from place import H, RIDGE, W

SEED = 23
KILL = (283, 104)
"""The kill at the track's far end, in the haze past the dead field's edge."""
KILL_PRINTS: list[tuple[float, float]] = [(322, 111), (312, 108), (302, 106), (292, 105)]
"""The wolves' prints, coming in along the far slope to the kill."""
RING_AT, RING_R = (13.9 * T, 6.6 * T), 30.0
"""The ring of prints at the scrub's edge: its centre past the snares' birch and its radius."""
DAMP_HEAP = (198, 150)
FF_MASTER = "tf_farmandfort/ff_master_tile_sheet.png"
DEER = "tf_animals/tf_animals/sheets/animals5.png"


def fog(density: int, walls: Image.Image) -> Image.Image:
    """Fog over the whole scene in soft drifts: `density` 3 is the day of the fog, 1 the haze it thins to. Walls are
    not cut away, the fog lies in front of everything."""
    del walls
    rng = random.Random(SEED + density)
    m, d = blank_mask()
    for _ in range(26 if density > 1 else 11):
        cx, cy = rng.randrange(-20, W // 2 + 20), rng.randrange(20, H // 2)
        rx, ry = rng.randrange(40, 110), rng.randrange(8, 22)
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    levels = {3: (26, 52, 78), 1: (14, 28)}[density]
    return soft(m, 5, levels, FOG)


def kill(walls: Image.Image) -> Image.Image:
    """A small deer down in the ash, at the far end's half size: the Animals pack's doe, its legs cut away and its
    head laid on the ground before it, rust where it bled, and the pack's bone where the rest was eaten."""
    img = Image.new("RGBA", (W // 2, H // 2))
    d = ImageDraw.Draw(img)
    x, y = KILL[0] // 2, KILL[1] // 2
    d.line((x - 6, y, x + 3, y), fill=(96, 58, 50, 150))
    d.line((x - 3, y + 1, x + 5, y + 1), fill=(96, 58, 50, 110))
    out = kit.up(img)
    deer = _downed_doe()
    out.alpha_composite(deer, (KILL[0] - deer.width // 2, KILL[1] - deer.height))
    bone = cut(FF_MASTER, (628, 51, 639, 62))
    out.alpha_composite(bone, (KILL[0] + 2, KILL[1] - bone.height - 3))
    return behind(out, walls)


def _downed_doe() -> Image.Image:
    """The doe's side frame (Animals sheet 5, 50x46 cells) laid down: the body above the legs, a dark outline row
    under it, the head and neck dropped to the same ground line in front, drained to the haze's tones."""
    frame = kit.load(DEER).crop((4 * 50, 46, 5 * 50, 92))
    body, head = frame.crop((17, 24, 41, 36)), frame.crop((9, 16, 24, 27))
    out = Image.new("RGBA", (34, 13))
    out.alpha_composite(body, (10, 0))
    out.alpha_composite(head, (0, 2))
    line = Image.new("RGBA", (22, 1), (53, 64, 72, 255))
    out.alpha_composite(line, (11, 12))
    return kit.grade(out, sat=0.45, mul=(1.0, 0.97, 0.95), bright=0.8, contrast=0.95)


def wolf_prints(walls: Image.Image) -> Image.Image:
    return behind(prints(KILL_PRINTS, 6.0), walls)


def ring_prints() -> Image.Image:
    """Prints round the scrub's edge, a ring walked more than once: a print every few pixels round a squashed circle."""
    path = [(RING_AT[0] + RING_R * math.cos(a / 8 * math.tau), RING_AT[1] + RING_R * 0.55 * math.sin(a / 8 * math.tau))
            for a in range(9)]
    return prints(path, 7.0)


def ridge_shapes(walls: Image.Image) -> Image.Image:
    """Five low grey shapes sat in a row along the ridge where the cart stood, faint in the haze, facing the camp."""
    m, d = blank_mask()
    cx, cy = int(RIDGE[0] / 2), int(RIDGE[1] / 2)
    for i in range(5):
        x = cx - 16 + i * 8
        d.rectangle((x, cy + 1, x + 2, cy + 4), fill=255)
        d.point((x + 1, cy), fill=255)
    return behind(soft(m, 0.4, (150, 230), (58, 64, 78)), walls)


def eyes() -> Image.Image:
    """Pairs of dull amber points out in the dark at the edge of the firelight, each pair a wolf."""
    img = Image.new("RGBA", (W // 2, H // 2))
    px = img.load()
    assert px is not None
    for x, y in ((232, 98), (236, 120), (104, 143), (138, 143), (196, 143)):
        for dx in (0, 3):
            px[x + dx, y] = (232, 138, 54, 255)
    return kit.up(img)


def wood_steam() -> Image.Image:
    """Slow puffs rising off the damp heap while the hand is on the stone, each higher one smaller and fainter."""
    m, d = blank_mask()
    rng = random.Random(SEED)
    for cx in (DAMP_HEAP[0] // 2 + 4, DAMP_HEAP[0] // 2 + 17, DAMP_HEAP[0] // 2 + 28):
        x = float(cx)
        for k in range(4):
            r = 2.6 - k * 0.45
            x += rng.uniform(-1.0, 1.0)
            d.ellipse((x - r, DAMP_HEAP[1] // 2 - 4 - k * 5 - r * 0.8, x + r, DAMP_HEAP[1] // 2 - 4 - k * 5 + r * 0.8),
                      fill=225 - k * 45)
    return soft(m, 0.8, (90, 150, 210), FOG)

