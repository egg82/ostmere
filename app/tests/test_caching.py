"""What a browser may keep: the bundle at a path naming its build for good, the shell page and the page config never
(docs/engineering.md, "A long cache only on a URL that changes with its content"), and /api/content until its build
changes, by validator."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ashfall_app.main import create_app
from ashfall_app.web import app as web, page


@pytest.fixture
def web_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    client = tmp_path / "client"
    client.mkdir()
    (client / "game.js").write_text("// js")
    (client / "game.css").write_text("/* css */")
    monkeypatch.setattr(page, "CLIENT", client)
    monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "absent"))
    monkeypatch.setenv("BUILD_VERSION", "main-abc-1")
    return TestClient(web.create_app())


def test_the_bundle_of_a_build_is_kept_for_good_and_the_shell_is_not(web_client: TestClient):
    shell = web_client.get("/")
    assert shell.status_code == 200 and "immutable" not in shell.headers.get("cache-control", ""), "control: the shell is not pinned"
    for name in ("game.js", "game.css"):
        r = web_client.get(f"/build/main-abc-1/{name}")
        assert r.status_code == 200 and r.headers["cache-control"] == "public, max-age=31536000, immutable", name
    missing = web_client.get("/build/main-abc-1/nope.js")
    assert missing.status_code == 404 and "immutable" not in missing.headers.get("cache-control", ""), "a 404 is never pinned"


def test_the_page_config_is_never_kept():
    r = TestClient(create_app()).get("/page-config.json")
    assert r.status_code == 200 and "max-age" not in r.headers.get("cache-control", "") and "immutable" not in r.headers.get("cache-control", "")


def test_content_answers_if_none_match_with_304():
    client = TestClient(create_app())
    first = client.get("/api/content")
    tag = first.headers.get("etag")
    assert first.status_code == 200 and tag, "an ETag names the build and the rules"
    again = client.get("/api/content", headers={"If-None-Match": tag})
    assert again.status_code == 304 and again.content == b"" and again.headers["etag"] == tag
    assert again.headers["x-ashfall-build"] == first.headers["x-ashfall-build"]
    assert client.get("/api/content", headers={"If-None-Match": '"other"'}).status_code == 200
    assert client.get("/api/content", headers={"If-None-Match": f'"other", {tag}'}).status_code == 304
