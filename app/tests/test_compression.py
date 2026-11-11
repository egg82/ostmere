"""Both servers compress a response to a client that accepts gzip, and the answer keeps its names and its bytes."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ashfall_app.main import create_app
from ashfall_app.web import app as web, page

GZIP = {"Accept-Encoding": "gzip"}
PLAIN = {"Accept-Encoding": "identity"}


@pytest.fixture
def bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    client = tmp_path / "client"
    client.mkdir()
    (client / "game.js").write_text("export const line = 'a long and repeated line';\n" * 200)
    (client / "game.css").write_text("/* css */")
    monkeypatch.setattr(page, "CLIENT", client)
    monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "absent"))
    monkeypatch.setenv("BUILD_VERSION", "main-abc-1")
    return "/build/main-abc-1/game.js"


def named(client: TestClient, path: str, server: str) -> None:
    packed, plain = client.get(path, headers=GZIP), client.get(path, headers=PLAIN)
    assert len(plain.content) > 1024, "control: the answer is over the minimum size"
    assert "content-encoding" not in plain.headers, "control: nothing is compressed for a client that asks for identity"
    assert packed.headers.get("content-encoding") == "gzip" and packed.content == plain.content, path
    assert packed.headers["x-ashfall-build"] and packed.headers.get_list("x-ashfall-server") == [server]


def test_the_app_compresses_its_content():
    named(TestClient(create_app()), "/api/content", "app")


def test_the_web_pods_compress_the_bundle(bundle: str):
    named(TestClient(web.create_app()), bundle, "web")


def test_a_small_answer_is_left_as_it_is():
    r = TestClient(create_app()).get("/healthz", headers=GZIP)
    assert r.status_code == 200 and "content-encoding" not in r.headers
