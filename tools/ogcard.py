"""The link-preview card: the front page's camp at night with the fire lit, cropped around the fire at a whole-number
scale, the title set in the page's own face.

    PYTHONPATH=tools/scene python tools/ogcard.py [OUT_DIR]   # writes OUT_DIR/art/og/ostmere.png (default $ASHFALL_ASSETS-og)

The card is never committed. Seed OUT_DIR onto the assets volume (the cluster repo's seed-assets Job); the page links it
as /assets/art/og/ostmere.png?h=<hash of the file> (ashfall_app/web/og.py), so a re-made card is a new URL and a chat
app's cached preview is not reused. The scene layers it composites are written to $ASHFALL_ASSETS, not to OUT_DIR.
Needs Pillow, fonttools with brotli (to read the page's woff2 font) and the Time Fantasy packs, like tools/scene.
"""
from __future__ import annotations

import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import build
import kit
from output import ASSETS, composite
from place import FIRE, H, W
from stages import STAGES

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "app" / "ashfall_app" / "static" / "fonts" / "im-fell-english-sc-latin.woff2"
CARD = (1200, 630)
SCALE = 3   # whole-number: the pixel art stays crisp
TITLE = "The Breaking of Ostmere"
INK = (217, 207, 192, 255)   # the page's --ink
TITLE_PX = 96
TITLE_TOP = 40
FIRE_FROM_TOP = 0.68   # the fire sits this far down the card, clear of the title


def moment() -> Image.Image:
    """The front page's canned camp (app/client/src/ui/camp-views.ts: fireback built, stool, stores) at night."""
    state = STAGES["7_fireback_built"].then({"feature:night"})
    entries = build.write_layers(random.Random(build.SEED))
    return composite(entries, state)


def crop_around_fire(scene: Image.Image) -> Image.Image:
    big = kit.resize(scene, (W * SCALE, H * SCALE))
    fx, fy = round(FIRE[0] * SCALE), round(FIRE[1] * SCALE)
    left = min(max(fx - CARD[0] // 2, 0), big.width - CARD[0])
    top = min(max(fy - round(CARD[1] * FIRE_FROM_TOP), 0), big.height - CARD[1])
    return big.crop((left, top, left + CARD[0], top + CARD[1]))


def title_font() -> ImageFont.FreeTypeFont:
    """The page's woff2, unpacked to a TTF by fonttools' own command (Pillow reads no woff2)."""
    with tempfile.TemporaryDirectory() as tmp:
        woff2 = Path(tmp) / FONT.name
        woff2.write_bytes(FONT.read_bytes())
        subprocess.run([sys.executable, "-m", "fontTools.ttLib.woff2", "decompress", str(woff2)], check=True)
        return ImageFont.truetype(str(woff2.with_suffix(".ttf")), TITLE_PX)


def shade_top(img: Image.Image, depth: int) -> Image.Image:
    """A fade of night down from the top edge, so the title reads over whatever the scene has there."""
    mask = Image.new("L", img.size, 0)
    rows = ImageDraw.Draw(mask)
    for y in range(depth):
        rows.line([(0, y), (img.width, y)], fill=round(200 * (1 - y / depth) ** 1.5))
    return Image.composite(Image.new("RGBA", img.size, (13, 14, 16, 255)), img, mask)


def set_title(img: Image.Image) -> Image.Image:
    img = shade_top(img, 260)
    draw = ImageDraw.Draw(img)
    font = title_font()
    width = draw.textlength(TITLE, font=font)
    if width > CARD[0] - 80:
        raise ValueError(f"the title is {width:.0f}px wide, too wide for the card")
    draw.text(((CARD[0] - width) / 2, TITLE_TOP), TITLE, font=font, fill=INK)
    return img


def make() -> Image.Image:
    card = set_title(crop_around_fire(moment()))
    assert card.size == CARD
    return card


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else f"{ASSETS}-og").expanduser() / "art" / "og"
    out.mkdir(parents=True, exist_ok=True)
    make().convert("RGB").save(out / "ostmere.png", optimize=True)
    print(f"og card {CARD[0]}x{CARD[1]} out={out / 'ostmere.png'}")


if __name__ == "__main__":
    main()
