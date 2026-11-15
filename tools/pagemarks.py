"""The journal's page marks (docs/design/journal.md, "Marks on the page"): Starshine Scribbles' "Stains and Damage"
overlays (CC BY 4.0, bought art outside the repo) cleaned of their scanned paper, recoloured where a kind needs it, and
scaled for the page, with a manifest of each kind's variants.

    python tools/pagemarks.py [SOURCE_DIR]   # writes $ASHFALL_ASSETS/journal/marks/

SOURCE_DIR defaults to ~/src/art/stains-and-damage, the sixteen overlays as downloaded.

The output is never committed: seed it onto the assets volume (app/tools/seed_assets.sh, kind `journal`). The page
reads /assets/journal/marks/manifest.json, {kind: [{src, w, h}]}, and draws each image with the parchment's multiply
blend, so white is no mark at all.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

SOURCE = Path("~/src/art/stains-and-damage").expanduser()
OUT = Path(os.environ.get("ASHFALL_ASSETS", "~/.local/share/ostmere/assets")).expanduser() / "journal" / "marks"
LONGEST = 512
"""Pixels on an image's longer side: a mark is at most about half the desktop page (540px) at twice its density."""


@dataclass(frozen=True)
class Pick:
    """One variant: the source overlay's number, the colour its ink is turned to (None keeps the scan's own), and the
    part of the scan used, as fractions (left, top, right, bottom): some scans hold a stain cut off by their own edge,
    or a scanner's edge line, that would show as a straight line on the page."""

    kind: str
    n: int
    ink: tuple[int, int, int] | None = None
    part: tuple[float, float, float, float] = (0, 0, 1, 1)


DRIED_BLOOD = (112, 18, 10)
SOOT = (38, 35, 33)
HAND_INK = (43, 36, 28)
MUD = (92, 70, 44)

NO_EDGE_LINE = (0, 0, 0.96, 1)
"""Scan 3 without the scanner's line down its right edge."""
SMEAR_TOP = (0, 0, 1, 0.55)
"""Scan 14's smear above the ruled ticks at its foot."""

PICKS = (
    Pick("blood", 1, DRIED_BLOOD), Pick("blood", 14, DRIED_BLOOD, SMEAR_TOP),
    Pick("soot", 4, SOOT), Pick("soot", 14, SOOT, SMEAR_TOP),
    Pick("water", 5), Pick("water", 6), Pick("water", 3, part=NO_EDGE_LINE),
    Pick("mud", 7, MUD), Pick("mud", 6, MUD),
    Pick("smudge", 14, HAND_INK, SMEAR_TOP), Pick("smudge", 7, HAND_INK),
    Pick("wear", 9), Pick("wear", 13, HAND_INK), Pick("wear", 16), Pick("wear", 3, part=NO_EDGE_LINE),
)


def mapped(gray: Image.Image, table: list[int]) -> Image.Image:
    """A greyscale image with each value looked up in `table` (256 entries)."""
    return Image.frombytes("L", gray.size, gray.tobytes().translate(bytes(table)))


def density(img: Image.Image) -> Image.Image:
    """How much mark each pixel holds, 0 to 255: the scan's alpha times how far the pixel is below its paper's
    brightness, so the scanned paper around a stain drops out and only the stain is left."""
    lum = ImageOps.grayscale(img.convert("RGB"))
    alpha = img.getchannel("A")
    seen = [v for v, a in zip(lum.tobytes(), alpha.tobytes(), strict=True) if a > 128]
    seen.sort()
    paper = seen[int(len(seen) * 0.97)] if seen else 255
    dark = seen[int(len(seen) * 0.02)] if seen else 0
    span = max(1, paper - dark)
    below = mapped(lum, [max(0, min(255, round(255 * (paper - v) / span))) for v in range(256)])
    return ImageChops.multiply(below, alpha)


FEATHER = 0.2
"""The share of a cut side over which the mark fades out, so a cut never shows as a straight edge."""


def feather(size: tuple[int, int], part: tuple[float, float, float, float]) -> Image.Image:
    """A mask, 255 inside, fading to 0 toward each side `part` cut (a side at the scan's own edge is left whole)."""
    w, h = size
    cut = (part[0] > 0, part[1] > 0, part[2] < 1, part[3] < 1)

    def ramp(i: int, n: int, low: bool, high: bool) -> float:
        reach = FEATHER * n
        f = 1.0
        if low:
            f = min(f, i / reach)
        if high:
            f = min(f, (n - 1 - i) / reach)
        return max(0.0, min(1.0, f))

    xs = [ramp(x, w, cut[0], cut[2]) for x in range(w)]
    ys = [ramp(y, h, cut[1], cut[3]) for y in range(h)]
    return Image.frombytes("L", size, bytes(round(255 * fx * fy) for fy in ys for fx in xs))


def made(pick: Pick, src: Path) -> Image.Image:
    img = Image.open(src).convert("RGBA")
    left, top, right, bottom = pick.part
    img = img.crop((round(left * img.width), round(top * img.height), round(right * img.width),
                    round(bottom * img.height)))
    d = ImageChops.multiply(density(img), feather(img.size, pick.part))
    if pick.ink is not None:
        out = Image.new("RGBA", img.size, (*pick.ink, 0))
    else:
        out = img.copy()
    out.putalpha(d)
    box = mapped(d, [255 if v > 10 else 0 for v in range(256)]).getbbox()
    if box is not None:
        out = out.crop(box)
    out.thumbnail((LONGEST, LONGEST), Image.Resampling.LANCZOS)
    return out


def main(source: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, list[dict[str, str | int]]] = {}
    for pick in PICKS:
        variant = len(manifest.get(pick.kind, [])) + 1
        name = f"{pick.kind}-{variant}.webp"
        img = made(pick, source / f"Stains And Damage {pick.n}.png")
        img.save(OUT / name, quality=82, method=6)
        manifest.setdefault(pick.kind, []).append({"src": name, "w": img.width, "h": img.height})
        print(f"tool=pagemarks event=made kind={pick.kind} file={name} source={pick.n} w={img.width} h={img.height}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"tool=pagemarks event=done out={OUT} files={len(PICKS) + 1}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else SOURCE)
