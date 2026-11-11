"""Draw the galaxy.click listing thumbnail: the opening scene's camp at night, the fire lit, and the title.

    python tools/galaxy_thumb.py                 # writes $ASHFALL_ASSETS/research/galaxy-thumb/galaxy-thumb.png
    python tools/galaxy_thumb.py --sheet         # also writes every candidate, at 500x300 and 250x150, and a sheet

Output is generated and holds Time Fantasy pixels, so it lives in the assets tree beside the scene's own output, never
in git (docs/engineering.md); the owner uploads it to galaxy.click by hand. Needs Pillow and the Time Fantasy packs.
Deterministic; the art is tools/scene/build.py's own layers (first-session ones only), under the front page's "dark"
grade, and the title is the page's: "The Breaking of" small over "Ostmere", IM Fell English SC in --ink with a black glow. Code draws only what the kit
lacks: embers, a wisp of smoke, the night closing in.
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "scene"))  # not a package; its modules import each other by bare name

import build
import grades
import kit
from place import FIRE, H, W

ASSETS = Path(os.environ.get("ASHFALL_ASSETS", "~/.local/share/ostmere/assets")).expanduser()
OUT = ASSETS / "research" / "galaxy-thumb"
FONT = ROOT / "app" / "ashfall_app" / "static" / "fonts" / "im-fell-english-sc-latin.woff2"
SIZE = (500, 300)
"""galaxy.click's recommended thumbnail; its list shows it at about half that."""
SEED = 7

NIGHT = (0x0D, 0x0E, 0x10)  # --night
INK = (0xD9, 0xCF, 0xC0)  # --ink, the ash
EMBERS = [(255, 255, 113), (255, 187, 71), (255, 93, 42), (255, 46, 23)]
"""The fire's own colours (fire_lit.png, as favicon.py takes them), hottest first."""
SMOKE = (150, 146, 140)

FLAME = ("hometown_TFcolor_update_8.24/_tfrecolor_8.24/1X/characters/!fires.png", (0, 0, 48, 32))
"""The kit's large campfire flame (first frame): stood on the scene's lit fire so the fire reads at thumbnail size."""

SHOWN = ("ruin", "cleared", "ring", "figure_by_fire", "firelight", "fire_lit", "ash")
"""The scene's layers this image draws: what a player sees once the first fire is lit, nothing later."""


@dataclass(frozen=True)
class Spec:
    """One composition: the scene crop (scene pixels) scaled by a whole number to fill SIZE, how far the night closes
    in on the fire (0 none, 1 all the way to --night at the edge), and where the title's centre sits on the output."""
    box: tuple[int, int, int, int]
    scale: int
    dark: float
    title_at: tuple[int, int]
    title_px: int
    """Ostmere's size; the line above it is set at about a quarter of it."""


CANDIDATES: dict[str, Spec] = {
    "camp": Spec(box=(112, 108, 362, 258), scale=2, dark=0.55, title_at=(250, 52), title_px=74),
    "whole": Spec(box=(-10, -6, 490, 294), scale=1, dark=0.85, title_at=(250, 40), title_px=64),
    "holdout": Spec(box=(80, 120, 330, 270), scale=2, dark=0.92, title_at=(160, 68), title_px=60),
}
CHOSEN = "holdout"


def scene_layers() -> dict[str, Image.Image]:
    """The scene's layers, built and baked exactly as build.py does (same seed, so the same ground and ruin)."""
    out: dict[str, Image.Image] = {}
    for layer in build.layers(random.Random(build.SEED)):
        if layer["id"] in SHOWN:
            out[layer["id"]] = build.bake(layer)
    return out


def flame() -> Image.Image:
    """The kit's flame, cropped to its pixels and doubled to the scene's 2x."""
    sheet, box = FLAME
    f = kit.load(sheet).crop(box)
    return kit.up(f.crop(f.getchannel("A").getbbox()))


def night_in(img: Image.Image, dark: float) -> Image.Image:
    """Pull everything outside the firelight toward --night: the camp is the one lit place."""
    lit = kit.radial((W, H), (FIRE[0] - 1.1 * kit.T, FIRE[1] - 8), 6 * kit.T, 255, int(255 * (1 - dark)), squash=0.75)
    night = Image.new("RGBA", (W, H), (*NIGHT, 255))
    return Image.composite(img, night, lit)


def smoke(rng: random.Random) -> Image.Image:
    """A thin wisp off the fire, on the art's 2 px grid: puffs that drift, widen and thin as they rise."""
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    y0 = FIRE[1] - 30
    for i in range(70):
        y = y0 - 2 * i
        x = FIRE[0] + 0.45 * i + 7 * math.sin(i / 7) * min(1, i / 20)
        size = 1 + i // 18
        a = int(100 * (1 - i / 70))
        for _ in range(2):
            if rng.random() < 0.35:
                continue  # a wisp breaks up as it goes
            px = int(x + rng.uniform(-2 * size, 2 * size)) // 2 * 2
            py = int(y) // 2 * 2
            d.rectangle((px, py, px + 2 * size - 1, py + 1), fill=(*SMOKE, a))
    return img


def embers(rng: random.Random, n: int) -> Image.Image:
    """Sparks thrown up from the fire, 2 px each like the art's pixels: hot near the flames, redder as they cool."""
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        rise = rng.random() ** 1.3
        drift = rng.gauss(0.2, 0.7)  # each spark's own lean, a little wind to the right, so they scatter
        x = FIRE[0] + rng.uniform(-10, 10) + rise * drift * 80
        y = FIRE[1] - 26 - rise * 120
        colour = EMBERS[min(3, int(rise * 4))]
        a = int(255 * (1 - 0.6 * rise))
        px, py = int(x) // 2 * 2, int(y) // 2 * 2
        d.rectangle((px, py, px + 1, py + 1), fill=(*colour, a))
    return img


def compose(layers: dict[str, Image.Image], spec: Spec) -> Image.Image:
    """The scene at night: the graded layers under the front page's grade, the night closing in, then the fire's light
    and flames ungraded on top (as the page draws the player's fire), then smoke, embers and ash."""
    rng = random.Random(SEED)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for name in ("ruin", "cleared", "ring", "figure_by_fire"):
        img.alpha_composite(layers[name])
    img = grades.apply(img, "dark").convert("RGBA")
    img = night_in(img, spec.dark)
    img = grades.screen(img, layers["firelight"])
    img.alpha_composite(smoke(rng))
    img.alpha_composite(layers["fire_lit"])
    f = flame()
    img.alpha_composite(f, (int(FIRE[0] - f.width / 2), int(FIRE[1] - f.height + 6)))
    img.alpha_composite(embers(rng, 26))
    ash = layers["ash"]
    img.alpha_composite(Image.composite(ash, Image.new("RGBA", ash.size), ImageChops.multiply(
        ash.getchannel("A"), Image.new("L", ash.size, 200))))
    left, top, right, bottom = spec.box
    assert ((right - left) * spec.scale, (bottom - top) * spec.scale) == SIZE, "crop x scale must fill SIZE"
    framed = Image.new("RGBA", (right - left, bottom - top), (*NIGHT, 255))
    framed.alpha_composite(img.crop(spec.box))  # a box past the scene's edge is padded with --night
    return kit.resize(framed, SIZE)


def _spaced(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, centre: tuple[float, float]) -> None:
    """One line of text, letter-spacing .08em, centred on `centre`."""
    gap = 0.08 * font.size
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + gap * (len(text) - 1)
    box = font.getbbox(text)
    x = centre[0] - total / 2
    y = centre[1] - (box[1] + box[3]) / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=255)
        x += w + gap


def title(img: Image.Image, spec: Spec) -> Image.Image:
    """'The Breaking of' small over 'Ostmere' large, as the front page sets it: IM Fell English SC, --ink, a soft black glow."""
    big = ImageFont.truetype(str(FONT), spec.title_px)
    lead = ImageFont.truetype(str(FONT), round(spec.title_px * 0.27))
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    cx, cy = spec.title_at
    _spaced(d, "The Breaking of", lead, (cx, cy - 0.5 * spec.title_px))
    _spaced(d, "Ostmere", big, (cx, cy + 0.12 * spec.title_px))
    glow = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(12))
    out = Image.composite(Image.new("RGBA", img.size, (0, 0, 0, 255)), img, ImageChops.multiply(
        glow, Image.new("L", img.size, 235)))
    out = Image.composite(Image.new("RGBA", img.size, (0, 0, 0, 255)), out, glow)
    return Image.composite(Image.new("RGBA", img.size, (*INK, 255)), out, mask)


def render(layers: dict[str, Image.Image], spec: Spec) -> Image.Image:
    return title(compose(layers, spec), spec).convert("RGB")


def small(img: Image.Image) -> Image.Image:
    """How a browser shows it in the list, at half size: smooth downscaling, as an <img> gets."""
    return kit.resize(img, (SIZE[0] // 2, SIZE[1] // 2), Image.Resampling.LANCZOS)


def contact_sheet(layers: dict[str, Image.Image], out: Path) -> None:
    """Every candidate at 500x300 with its 250x150 beside it."""
    names = list(CANDIDATES)
    sheet = Image.new("RGB", (SIZE[0] + SIZE[0] // 2 + 36, len(names) * (SIZE[1] + 30) + 12), (0x35, 0x36, 0x3A))
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(names):
        img = render(layers, CANDIDATES[name])
        img.save(out / f"{name}.png")
        small(img).save(out / f"{name}-250.png")
        y0 = 12 + i * (SIZE[1] + 30)
        sheet.paste(img, (12, y0))
        sheet.paste(small(img), (SIZE[0] + 24, y0))
        d.text((12, y0 + SIZE[1] + 4), name, fill=(230, 230, 230))
    sheet.save(out / "contact-sheet.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", action="store_true", help="also write every candidate and a contact sheet")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    layers = scene_layers()
    render(layers, CANDIDATES[CHOSEN]).save(OUT / "galaxy-thumb.png")
    if args.sheet:
        contact_sheet(layers, OUT)
    print(f"galaxy-thumb chosen={CHOSEN} out={OUT / 'galaxy-thumb.png'}")


if __name__ == "__main__":
    main()
