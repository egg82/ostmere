"""People in the scene: a Time Fantasy side-view battler frame, grimed (drained clothes, the skin kept close to the
sprite's own), cropped and stood with its feet on a spot. The battler sheets have no back view, so the player seen from
behind is the same hooded figure's frame on the walking-character sheets, which have one."""
from __future__ import annotations

from collections.abc import Callable, Iterable

from PIL import Image, ImageChops

import kit
from place import canvas, put

PLAYER = "2_3"
"""Side-view battler set 2, character 3: a hooded figure in a drab coat."""
PLAYER_SHEET = ("timefantasy_characters/timefantasy_characters/sheets/chara2.png", 2)
"""The same hooded figure on the walking-character sheet (character set 2 is battler set 2): its back view."""
SKIN = kit.Grade(sat=0.4, mul=(1.0, 1.0, 1.0), bright=0.95, contrast=0.95)
"""Skin and face: close to the sprite's own tones, picked out of the figure by hue."""
CLOTHES = kit.Grade(sat=0.6, mul=(1.03, 1.0, 0.92), bright=0.95, contrast=1.05)

Held = tuple[Image.Image, float, float]
"""A prop in the figure's hands: the sprite and its top-left, in pixels from the feet."""


def figure(frame: str, feet: tuple[float, float], flip: bool = False,
           tweak: Callable[[Image.Image], Image.Image] | None = None, held: Iterable[Held] = (),
           char: str = PLAYER, behind: Iterable[Held] = ()) -> Image.Image:
    """A pose with the bottom centre of its drawn pixels (the shadow under the feet) at `feet`: the battler frames
    sit their bodies at different offsets, so anchoring the frame itself would make the figure jump between poses.
    Lifted a shade after the grime so a dark coat still reads against the dark wall. `tweak` reshapes the cropped
    sprite (a bowed head, no shadow for a seat); `held` puts props in its hands, `behind` props it holds across its
    body, drawn under it."""
    return stand(kit.battler(char, frame), feet, flip, tweak, held, behind)


def from_behind(feet: tuple[float, float], tweak: Callable[[Image.Image], Image.Image] | None = None,
                held: Iterable[Held] = ()) -> Image.Image:
    """The player with the back to the camp: the walking sheet's standing frame facing away."""
    return stand(kit.walker(*PLAYER_SHEET, "up"), feet, tweak=tweak, held=held)


def stand(src: Image.Image, feet: tuple[float, float], flip: bool = False,
          tweak: Callable[[Image.Image], Image.Image] | None = None, held: Iterable[Held] = (),
          behind: Iterable[Held] = ()) -> Image.Image:
    """`figure` for any sprite frame: graded, cropped and stood with its feet on a spot."""
    sprite = kit.grade(src, **CLOTHES)
    skin = Image.eval(src.convert("RGB").convert("HSV").getchannel("H"), lambda h: 255 if h < 40 else 0)   # hue 0-50 deg
    warm = Image.eval(src.convert("RGB").convert("HSV").getchannel("S"), lambda v: 255 if v > 100 else 0)
    bright = Image.eval(src.convert("RGB").convert("HSV").getchannel("V"), lambda v: 255 if v > 150 else 0)
    mask = ImageChops.multiply(ImageChops.multiply(skin, warm), bright)
    sprite = kit.keep_alpha(sprite, Image.composite(kit.grade(src, **SKIN).convert("RGB"), sprite.convert("RGB"), mask))
    if flip:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    box = sprite.getchannel("A").getbbox()
    assert box is not None
    sprite = sprite.crop(box)
    if tweak:
        sprite = tweak(sprite)
    img = canvas()
    for prop, dx, dy in behind:
        put(img, prop, feet[0] + dx, feet[1] + dy)
    put(img, sprite, feet[0] - sprite.width / 2, feet[1] - sprite.height)
    for prop, dx, dy in held:
        put(img, prop, feet[0] + dx, feet[1] + dy)
    return img
