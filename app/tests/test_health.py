from pathlib import Path

from fastapi.testclient import TestClient

from ashfall_app.web import page as page_files
from ashfall_app.main import create_app, read_changes
from pytest import MonkeyPatch


def test_healthz_reports_the_build(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("BUILD_VERSION", "abc123")
    response = TestClient(create_app()).get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "abc123"}


def test_index_serves_the_page():
    response = TestClient(create_app()).get("/")
    assert response.status_code == 200
    assert "<title>The Breaking of Ostmere</title>" in response.text


def test_changes_read_from_the_file_ci_writes(tmp_path: Path):
    f = tmp_path / "changes.txt"
    f.write_text("2026-10-11 ashfall: a thing\n2026-10-10 ashfall: an older thing\n\n")
    assert [c.subject for c in read_changes(f)] == ["ashfall: a thing", "ashfall: an older thing"]
    assert read_changes(f)[0].date == "2026-10-11"


def test_changes_empty_without_the_file(tmp_path: Path):
    assert read_changes(tmp_path / "missing.txt") == []


def test_assets_served_from_the_volume_with_types_and_long_cache(tmp_path: Path, monkeypatch: MonkeyPatch):
    (tmp_path / "art" / "scene").mkdir(parents=True)
    (tmp_path / "audio" / "sfx").mkdir(parents=True)
    (tmp_path / "art" / "scene" / "ruin.png").write_bytes(b"\x89PNG")
    (tmp_path / "art" / "scene" / "manifest.json").write_text("{}")
    (tmp_path / "audio" / "sfx" / "fire.ogg").write_bytes(b"OggS")
    monkeypatch.setenv("ASSETS_DIR", str(tmp_path))
    client = TestClient(create_app())
    for path, content_type in [
        ("art/scene/ruin.png", "image/png"),
        ("audio/sfx/fire.ogg", "audio/ogg"),
        ("art/scene/manifest.json", "application/json"),
    ]:
        response = client.get(f"/assets/{path}")
        assert response.status_code == 200
        assert response.headers["content-type"] == content_type
        assert response.headers["cache-control"] == "public, no-cache"   # a reseed keeps names: revalidate, never pin
        again = client.get(f"/assets/{path}", headers={"if-none-match": response.headers["etag"]})
        assert again.status_code == 304
    assert client.get("/assets/art/scene/nope.png").status_code == 404


def test_assets_cannot_escape_the_root(tmp_path: Path, monkeypatch: MonkeyPatch):
    root = tmp_path / "root"
    (root / "art").mkdir(parents=True)
    (tmp_path / "secret.json").write_text("{}")
    monkeypatch.setenv("ASSETS_DIR", str(root))
    client = TestClient(create_app())
    for path in ["/assets/../secret.json", "/assets/%2e%2e/secret.json", "/assets/art/..%2f..%2fsecret.json"]:
        assert client.get(path).status_code == 404


def test_assets_404_and_app_starts_without_the_volume(tmp_path: Path, monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "absent"))
    client = TestClient(create_app())
    assert client.get("/assets/art/scene/ruin.png").status_code == 404
    assert client.get("/healthz").status_code == 200


def test_favicon_set_is_served() -> None:
    client = TestClient(create_app())
    for path, kind in [("/favicon.ico", "image/x-icon"), ("/icons/favicon.svg", "image/svg+xml"),
                       ("/icons/apple-touch-icon.png", "image/png")]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["content-type"].startswith(kind), path
    page = client.get("/").text
    assert 'href="/favicon.ico"' in page and "/icons/favicon.svg" in page and "/icons/apple-touch-icon.png" in page


def test_the_page_loads_the_bundle_of_its_own_build(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Mid-deploy a page and its bundle can come from two builds: the page names its build in the bundle's path, so the
    other build answers 404 there (and the page reloads once, static/index.html) instead of running a foreign bundle."""
    (tmp_path / "game.js").write_text("// js")
    (tmp_path / "game.css").write_text("/* css */")
    monkeypatch.setattr(page_files, "CLIENT", tmp_path)
    monkeypatch.setenv("BUILD_VERSION", "main-abc-1")
    client = TestClient(create_app())
    page = client.get("/").text
    assert "{{build}}" not in page
    for name in ["game.js", "game.css"]:
        assert f'"/build/main-abc-1/{name}" onerror="bootFailed()"' in page
        assert client.get(f"/build/main-abc-1/{name}").status_code == 200
        assert client.get(f"/build/main-abc-0/{name}").status_code == 404   # another build's path
        assert client.get(f"/build/{name}").status_code == 404   # no unversioned path
