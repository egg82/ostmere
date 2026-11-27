"""The world map's stamps (app/ashfall_app/api/contract/map.txt, "MAP"): the Widman 2.1 PNG pack's engraved map symbols
(K.M. Alexander, CC0; docs/research/art/art-sourcing.md), one folder per stamp kind, cropped to their ink, with a manifest
of each kind's variants.

    python tools/mapstamps.py [SOURCE_DIR]   # writes $ASHFALL_ASSETS/art/map/

SOURCE_DIR defaults to ~/src/art/widman, the pack's "Widman Cartography Brushes 2.1 PNG Pack" folder as downloaded.

The output is never committed: seed it onto the assets volume (app/tools/seed_assets.sh, kind `art`). The page reads
/assets/art/map/manifest.json, {stamp: [{src, w, h}]}, and draws each image as a mask filled with its ink, so only the
alpha is used.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

SOURCE = Path("~/src/art/widman").expanduser()
OUT = Path(os.environ.get("ASHFALL_ASSETS", "~/.local/share/ostmere/assets")).expanduser() / "art" / "map"

FOLDERS = {
    "village": "Settlements/Villages",
    "town": "Settlements/Towns",
    "city": "Settlements/Cities",
    "fort": "Settlements/Forts",
    "stronghold": "Settlements/Fortified Cities",
    "hill_village": "Landforms/Unique Landforms/Hills with Villages",
    "crossing": "Settlements/River Crossings/North South River",
    "mountain": "Landforms/Mountains",
    "range": "Landforms/Mountain Range",
    "forest": "Trees/Forest",
    "tree": "Trees/Individual Trees",
}
"""Each stamp kind (api/world/map_models.py, Stamp) and the pack's folder its variants come from."""


def made(src: Path) -> Image.Image:
    """The stamp cropped to its ink, black on transparent."""
    img = Image.open(src).convert("RGBA")
    alpha = img.getchannel("A")
    box = alpha.point([0 if v < 8 else 255 for v in range(256)]).getbbox()
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.putalpha(alpha)
    return out if box is None else out.crop(box)


def main(source: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, list[dict[str, str | int]]] = {}
    for kind, folder in FOLDERS.items():
        files = sorted((source / folder).glob("*.png"))
        if not files:
            raise SystemExit(f"tool=mapstamps event=failed kind={kind} reason=no_pngs folder={folder!r}")
        for n, src in enumerate(files, start=1):
            name = f"{kind}-{n}.png"
            img = made(src)
            img.save(OUT / name, optimize=True)
            manifest.setdefault(kind, []).append({"src": name, "w": img.width, "h": img.height})
        print(f"tool=mapstamps event=made kind={kind} variants={len(files)}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"tool=mapstamps event=done out={OUT} files={sum(len(v) for v in manifest.values()) + 1}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else SOURCE)
