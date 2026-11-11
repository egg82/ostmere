"""Draw the favicon set: a tiny campfire on the night colour, on a real 16x16 pixel grid.

    python tools/favicon.py                      # writes app/ashfall_app/static/icons/
    python tools/favicon.py --sheet DIR          # also writes every candidate, and a contact sheet, into DIR

Output is generated: it lives in static/icons/ and is never hand-edited (docs/engineering.md). Needs Pillow.
Deterministic; the colours are the scene's (fire_lit.png) and the page's --night / --ink tokens.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "app" / "ashfall_app" / "static" / "icons"

PALETTE: dict[str, tuple[int, int, int]] = {
    ".": (0x0D, 0x0E, 0x10),  # --night
    "R": (255, 46, 23),
    "O": (255, 93, 42),
    "A": (255, 187, 71),
    "Y": (255, 255, 113),
    "L": (143, 69, 67),  # logs, from the scene's warm browns
    "l": (166, 101, 62),
    "S": (96, 98, 104),  # the ruin's cool stone, never brown
    "s": (62, 64, 70),
    "w": (217, 207, 192),  # --ink, the ash
    "e": (120, 114, 106),  # a dimmer fleck
}

CANDIDATES: dict[str, tuple[str, ...]] = {
    "flame": (
        "................",
        "......w.........",
        ".......O........",
        ".......OO.......",
        "......OOO.......",
        "......OOOO......",
        ".....OOOOOO.....",
        ".....OOAOOO.....",
        "....OOOAAOOO....",
        "....OOAAAAOO....",
        "....OOAAYAOO..w.",
        "....ROAAYYAOR...",
        ".....ROAYYAOR...",
        ".....RROAAORR...",
        "......RRRRR.....",
        "................",
    ),
    "ring": (
        "................",
        "................",
        ".......O........",
        ".......OO.......",
        "......OOO...w...",
        "......OOAO......",
        ".....OOAAOO.....",
        ".....OAAYAO.....",
        ".....OAYYAO.....",
        "....ROAYYAOR....",
        "..SSRRAAARRSS...",
        ".SsLLLRRRLLLsS..",
        ".SsllLLLLLllsS..",
        "..SSSsSSSsSSS...",
        "................",
        "................",
    ),
    "ember": (
        "................",
        "...w............",
        "..........e.....",
        "................",
        "......w.........",
        "................",
        ".......O........",
        "......OAO.......",
        ".....OAYAO......",
        ".....OAYAO......",
        "......OAO.......",
        "....RRROORR.....",
        "...LLLRRRLLL....",
        "..lLLLLLLLLLl...",
        "................",
        "................",
    ),
}

CHOSEN = "flame"
SHEET_BG = {"light tab": (0xDE, 0xE1, 0xE6), "dark tab": (0x35, 0x36, 0x3A)}


def render(grid: tuple[str, ...], scale: int = 1, pad: int = 0, size: int | None = None) -> Image.Image:
    """The grid as pixels, each cell a scale x scale block, centred on a night canvas of `size` (or grid + pad)."""
    n = len(grid)
    assert all(len(row) == n for row in grid), "grid must be square"
    side = size if size is not None else n * scale + 2 * pad
    img = Image.new("RGB", (side, side), PALETTE["."])
    off = (side - n * scale) // 2
    px = img.load()
    assert px is not None
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            for dy in range(scale):
                for dx in range(scale):
                    px[off + x * scale + dx, off + y * scale + dy] = PALETTE[ch]
    return img


def svg(grid: tuple[str, ...]) -> str:
    """Crisp vector rects: one night backdrop, then a run of same-colour cells per row."""
    n = len(grid)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">',
        f'<rect width="{n}" height="{n}" fill="#{_hex(PALETTE["."])}"/>',
    ]
    for y, row in enumerate(grid):
        x = 0
        while x < n:
            ch = row[x]
            run = 1
            while x + run < n and row[x + run] == ch:
                run += 1
            if ch != ".":
                out.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="#{_hex(PALETTE[ch])}"/>')
            x += run
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _hex(c: tuple[int, int, int]) -> str:
    return "%02x%02x%02x" % c


def ico(grid: tuple[str, ...], path: Path) -> None:
    """A 16 and a 32 entry, each already on whole pixels: Pillow would otherwise resample one image down."""
    entries = [render(grid, 1), render(grid, 2)]
    blobs: list[bytes] = []
    for im in entries:
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        blobs.append(buf.getvalue())
    head = bytes([0, 0, 1, 0, len(blobs), 0])
    offset = 6 + 16 * len(blobs)
    table = b""
    for im, blob in zip(entries, blobs):
        table += bytes([im.width, im.height, 0, 0]) + (1).to_bytes(2, "little") + (32).to_bytes(2, "little")
        table += len(blob).to_bytes(4, "little") + offset.to_bytes(4, "little")
        offset += len(blob)
    path.write_bytes(head + table + b"".join(blobs))


def write_set(grid: tuple[str, ...], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    # 32 is the same grid doubled, so both sizes are the one drawing on whole pixels.
    ico(grid, out / "favicon.ico")
    (out / "favicon.svg").write_text(svg(grid))
    render(grid, 10, size=180).save(out / "apple-touch-icon.png")


def contact_sheet(out: Path) -> None:
    """Every candidate at 16 and 32 actual size, and at 8x, on a light and a dark tab bar."""
    out.mkdir(parents=True, exist_ok=True)
    cell = 16 * 8 + 24
    names = list(CANDIDATES)
    sheet = Image.new("RGB", (cell * len(names), 2 * (cell + 60)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for row, (label, bg) in enumerate(SHEET_BG.items()):
        y0 = row * (cell + 60)
        d.rectangle((0, y0, sheet.width, y0 + cell + 60), fill=bg)
        fg = (20, 20, 20) if row == 0 else (230, 230, 230)
        for i, name in enumerate(names):
            x0 = i * cell
            grid = CANDIDATES[name]
            sheet.paste(render(grid, 8), (x0 + 12, y0 + 8))
            sheet.paste(render(grid, 1), (x0 + 12, y0 + 16 * 8 + 18))
            sheet.paste(render(grid, 2), (x0 + 12 + 40, y0 + 16 * 8 + 18))
            d.text((x0 + 12, y0 + 16 * 8 + 44), f"{name} ({label})", fill=fg)
        render(CANDIDATES[CHOSEN], 1).save(out / "chosen-16.png")
    for name, grid in CANDIDATES.items():
        render(grid, 8).save(out / f"{name}-8x.png")
        render(grid, 2).save(out / f"{name}-32.png")
    sheet.save(out / "contact-sheet.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sheet", type=Path, help="also write the candidates and a contact sheet here")
    args = ap.parse_args()
    write_set(CANDIDATES[CHOSEN], ICONS)
    if args.sheet:
        contact_sheet(args.sheet)


if __name__ == "__main__":
    main()
