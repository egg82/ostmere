"""The web manifest names the icons an installed app needs, and each file is a PNG of the size it claims."""

import struct
from pathlib import Path

from fastapi.testclient import TestClient

from ashfall_app.web import app as web
from ashfall_app.web import page

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WANTED = {("192x192", "any"), ("512x512", "any"), ("512x512", "maskable")}


def png_size(path: Path) -> tuple[int, int]:
    head = path.read_bytes()[:24]
    assert head[:8] == PNG_MAGIC, f"{path.name} is not a PNG"
    return struct.unpack(">II", head[16:24])


def test_png_size_reads_a_known_file_and_refuses_a_non_png(tmp_path: Path):
    assert png_size(page.ICONS / "icon-192.png") == (192, 192)
    bad = tmp_path / "x.png"
    bad.write_bytes(b"not a png at all, just text padding")
    try:
        png_size(bad)
    except AssertionError:
        return
    raise AssertionError("a non-PNG passed")


def test_the_manifest_lists_the_three_icons_and_each_file_is_a_png_of_its_size():
    manifest = TestClient(web.create_app()).get("/manifest.webmanifest").json()
    listed = {(i["sizes"], i.get("purpose")): i for i in manifest["icons"] if i["type"] == "image/png"}
    assert WANTED <= set(listed)
    for (sizes, _), icon in listed.items():
        assert icon["src"].startswith("/icons/")
        width, height = png_size(page.ICONS / icon["src"].removeprefix("/icons/"))
        assert f"{width}x{height}" == sizes
