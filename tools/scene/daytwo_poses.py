"""Day two's poses: N1 at each of her tasks, on the stool, asleep by the fire and leaving through the gap, all from the
same walking-character frames as day one's N1 and grimed and outlined the same way; and the player stood aside while
the stool changes hands. The kit has no working frames for her sheet, so a task is her frame plus what she carries,
and sleep is the bed sprites' convention (the back of her head on the pillow, the blanket over the rest).
Story spoilers (content/team/day-two.md, Art): never shown to the owner."""
from __future__ import annotations

from collections.abc import Callable, Iterable

from PIL import Image, ImageOps

import kit
import props
from daytwo import bedroll
from dayone_poses import N1, N1_GAP, drab, outlined
from figures import Held, figure, stand
from kit import ASH_B, FORT, T
from place import SEAT, canvas, put

SCRUB = (13.35 * T, 6.1 * T)
"""Where she forages: crouched at the scrub's edge past the birch, above the snares."""
TO_HEAP = (5.45 * T, 6.75 * T)
"""Where she brings wood in: the open ground between the larder and the fire, walking toward the damp heap."""
TO_STONES = (12.35 * T, 6.0 * T)
"""Where she brings stones in: walking toward the carried-in stones from the ruin's side."""
AT_LOG = (12.95 * T, 6.55 * T)
"""Where she cuts: at the felled birch's sawn end by the stump, facing back along it, clear of the stool."""
BY_EMBERS = (11.95 * T, 7.7 * T)
"""Her bedroll's top-left on the nights she sleeps in the open: by the fire on the player's side, past the stool."""
GIVING = (12.45 * T, 8.3 * T)
"""Where the player stands while the stool changes hands: at the stool's right, facing it."""


Who = tuple[str, int]
"""A walking-character sheet and the character on it."""


def person(who: Who, facing: str, feet: tuple[float, float], col: int = 1, drop: int = 0, held: Iterable[Held] = (),
           tweak: Callable[[Image.Image], Image.Image] | None = None) -> Image.Image:
    """One of the camp's people, grimed and outlined as day one's N1 is, on a spot."""
    return outlined(drab(stand(kit.walker(*who, facing, col=col, drop=drop), feet, tweak=tweak, held=held)))


def _her(facing: str, feet: tuple[float, float], col: int = 1, drop: int = 0, held: Iterable[Held] = (),
         tweak: Callable[[Image.Image], Image.Image] | None = None) -> Image.Image:
    return person(N1, facing, feet, col=col, drop=drop, held=held, tweak=tweak)


def _piece(sheet: str, c: float, r: float, w: float = 1, h: float = 1) -> Image.Image:
    t = kit.tile(kit.load(sheet), c, r, w, h)
    box = t.getchannel("A").getbbox()
    assert box is not None
    return t.crop(box)


def _rock(sprite: Image.Image, lean: int = 2) -> Image.Image:
    """The stool rocking under her: everything above her lap shifted `lean` pixels toward the fire."""
    out = Image.new("RGBA", sprite.size)
    lap = int(sprite.height * 0.62)
    out.alpha_composite(sprite.crop((0, lap, sprite.width, sprite.height)), (0, lap))
    out.alpha_composite(sprite.crop((0, 0, sprite.width, lap)), (-lean, 0))
    return out


def n1_rocking() -> Image.Image:
    """On the stool, facing the fire, the stool rocking: the seated frame (cut short, no shadow), leaning."""
    return _her("left", SEAT, drop=7, tweak=lambda s: _rock(props.seated(s)))


def foraging(who: Who = N1) -> Image.Image:
    """Crouched at the scrub's edge, facing into it: a frame cut short low down reads as crouching at game scale, and
    the shadow the cut took off is laid back under her."""
    img = canvas()
    put(img, props.figure_shadow(30), SCRUB[0] - 15, SCRUB[1] - 7)
    img.alpha_composite(person(who, "right", SCRUB, drop=9))
    return img


def gathering(who: Who = N1) -> Image.Image:
    """Walking in with an armful of the dead wood held in front, toward the heap."""
    sticks = _piece(ASH_B, 7, 15)
    return person(who, "right", TO_HEAP, col=0, held=[(sticks, -4, -32)])


def scavenging(who: Who = N1) -> Image.Image:
    """Walking in with a stone from the ruin held in front, toward the stones."""
    stone = _piece(ASH_B, 0, 2)
    return person(who, "left", TO_STONES, col=2, held=[(stone, -stone.width + 6, -28)])


def cutting(who: Who = N1) -> Image.Image:
    """At the felled birch, her own hatchet (Farm and Fort's loose one) coming down on it from her front hand."""
    hatchet = ImageOps.mirror(_piece(FORT, 5, 15.1, 0.85, 0.65))
    return person(who, "left", AT_LOG, col=1, held=[(hatchet, -4 - hatchet.width, -26)])


def n1_leaving() -> Image.Image:
    """Walking out through the gap, her back to the camp."""
    return _her("up", N1_GAP, col=0)


def n1_asleep() -> Image.Image:
    """Asleep on her bedroll by the fire: the back of her head on the pillow end, the blanket over the rest."""
    roll = bedroll()
    head = drab(kit.walker(*N1, "up"))
    box = head.getchannel("A").getbbox()
    assert box is not None
    head = head.crop((box[0], box[1], box[2], box[1] + 22)).transpose(Image.Transpose.ROTATE_90)
    img = canvas()
    put(img, props.figure_shadow(roll.width + 4), BY_EMBERS[0] - 2, BY_EMBERS[1] + roll.height - 7)
    put(img, roll, BY_EMBERS[0], BY_EMBERS[1])
    put(img, head, BY_EMBERS[0] - 6, BY_EMBERS[1] + (roll.height - head.height) / 2 - 2)
    return img


def giving_stool() -> Image.Image:
    """The player up off the stool and stood at its right, facing it."""
    return figure("status (1)", GIVING)
