"""The assets volume's cache headers (ashfall_app/web/page.py): a scene layer's URL carries `?h=` (tools/scene/build.py),
and only a request whose `h` is the served file's own content hash is told the copy never changes."""

import hashlib
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ashfall_app.web import app as web, page

IMMUTABLE = "public, max-age=31536000, immutable"
REVALIDATE = "public, no-cache"


def prefix(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


@pytest.fixture
def assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    volume = tmp_path / "assets"
    (volume / "scene").mkdir(parents=True)
    (volume / "scene" / "layer.png").write_bytes(b"\x89PNG one")
    (volume / "scene" / "manifest.json").write_text("{}")
    monkeypatch.setenv("ASSETS_DIR", str(volume))
    monkeypatch.setattr(page, "CLIENT", tmp_path / "no-client")
    monkeypatch.setenv("BUILD_VERSION", "main-abc-1")
    return volume


def cache_control(client: TestClient, url: str) -> str | None:
    response = client.get(url)
    assert response.status_code == 200, url
    return response.headers.get("cache-control")


def test_a_layer_asked_for_by_its_own_hash_is_immutable(assets: Path):
    client = TestClient(web.create_app())
    assert cache_control(client, f"/assets/scene/layer.png?h={prefix(b'\x89PNG one')}") == IMMUTABLE


def test_a_layer_asked_for_by_another_hash_or_none_is_revalidated(assets: Path):
    client = TestClient(web.create_app())
    assert cache_control(client, f"/assets/scene/layer.png?h={prefix(b'a newer layer')}") == REVALIDATE
    assert cache_control(client, "/assets/scene/layer.png") == REVALIDATE
    assert cache_control(client, "/assets/scene/layer.png?h=") == REVALIDATE


def test_the_manifest_is_revalidated(assets: Path):
    client = TestClient(web.create_app())
    assert cache_control(client, "/assets/scene/manifest.json") == REVALIDATE
    assert cache_control(client, f"/assets/scene/manifest.json?h=stale") == REVALIDATE


def test_a_file_replaced_on_disk_is_hashed_again(assets: Path):
    client = TestClient(web.create_app())
    layer = assets / "scene" / "layer.png"
    old, new = b"\x89PNG one", b"\x89PNG two!"
    assert cache_control(client, f"/assets/scene/layer.png?h={prefix(old)}") == IMMUTABLE
    layer.write_bytes(new)
    stat = layer.stat()
    os.utime(layer, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10_000_000_000))
    assert cache_control(client, f"/assets/scene/layer.png?h={prefix(old)}") == REVALIDATE
    assert cache_control(client, f"/assets/scene/layer.png?h={prefix(new)}") == IMMUTABLE
