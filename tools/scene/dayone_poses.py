"""Day one's poses: the player's jobs away from the fire (the snares, the gap, the builds, sitting up at night) and N1's
two, from a walking-character sheet grimed the same way as the player.
Story spoilers (content/team/day-one.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageEnhance, ImageFilter

import dayone
import kit
import props
from figures import figure, from_behind, stand
from kit import T
from place import SEAT

N1 = ("timefantasy_characters/timefantasy_characters/sheets/npc2.png", 1)
"""A walking-character sheet and the character on it: a woman with long brown hair, a pale blouse and a skirt. The same
grime as the player, then drained further, so no bright dye stands out in the ash."""
LOOKOUT = (9.55 * T, 4.92 * T)
"""Just inside the fallen beam in the gap, looking out toward the ridge (any higher and the head meets the strip)."""
N1_GAP = (9.3 * T, 4.85 * T)
"""N1 walking: in the gap, over the fallen beam."""
N1_SEAT = (SEAT[0] + 1.05 * T, SEAT[1] + 0.35 * T)
"""N1's seat: the player's side of the fire (D-62), beside the player on the stool and a little forward, clear of the
ring's stones, the stool and the player."""
WORK = {"lean_to": (2.45 * T, 8.0 * T), "larder": (4.95 * T, 6.55 * T), "smoke_rack": (6.0 * T, 8.85 * T)}
"""Where the figure stands to build each thing, facing it."""


def _pole() -> Image.Image:
    """A length of pole held across both hands, as the kit draws a thin pole: lit along its top, outlined in navy, its
    cut ends showing the wood's pale face."""
    return kit.up(kit.pixels(["n" * 32, "e" + "h" * 30 + "e", "n" + "m" * 30 + "n", "n" * 32],
                             {"n": dayone.NAVY, "h": dayone.WOOD_HI, "m": dayone.WOOD_MID, "e": dayone.STRAW}))


def sitting_up() -> Image.Image:
    """Up late on the stool, the seated pose."""
    return figure("status (1)", SEAT, tweak=props.seated)


def looking_out() -> Image.Image:
    """Standing in the gap with the back to the camp, facing out at the ridge."""
    return from_behind(LOOKOUT)


def building(what: str) -> Image.Image:
    """The hit frame (arms out) at the thing being built, a pole across the hands."""
    return build_at(WORK[what])


def build_at(spot: tuple[float, float], flip: bool = False) -> Image.Image:
    """`flip` faces the work on the figure's right."""
    return figure("hit (2)", spot, flip=flip, behind=[(_pole(), -32, -32)])


def snaring() -> Image.Image:
    """Crouched at the first snare's run, facing it."""
    sapling = dayone.SNARES[0]
    return figure("crouch (3)", (sapling[0] - 0.3 * T, sapling[1] + 0.75 * T), flip=True)


def drab(img: Image.Image) -> Image.Image:
    return kit.keep_alpha(img, ImageEnhance.Color(img.convert("RGB")).enhance(0.55))


def n1_walking() -> Image.Image:
    """Walking in through the gap toward the fire."""
    return drab(stand(kit.walker(*N1, "left", col=0), N1_GAP))


def outlined(img: Image.Image) -> Image.Image:
    """A dark one-pixel outline round the figure, so it holds against the ash and the ring at phone width."""
    out = Image.new("RGBA", img.size, (22, 18, 20, 255))
    out.putalpha(kit.point(img.getchannel("A"), lambda v: 255 if v else 0).filter(ImageFilter.MaxFilter(3)))
    out.alpha_composite(img)
    return out


def n1_by_fire() -> Image.Image:
    return outlined(drab(stand(kit.walker(*N1, "left", drop=6), N1_SEAT)))
