"""The web pods' server (ashfall_app/web/app.py): the page's files, with nothing that needs the database or a secret, and
every route of the app on a path the edge sends to the app instead (or a file the web pods serve too)."""

import ast
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ashfall_app import main
from ashfall_app.web import app as web, page
from tests import test_boundaries as boundaries

ALLOWED = {"web", "build_header", "head", "logs", "old_host"}
NEVER = {"psycopg", "psycopg_pool", "sqlalchemy", "alembic"}   # the database's drivers: the app's secret is its DSN


@runtime_checkable
class _Included(Protocol):
    """An included router as FastAPI keeps it in app.routes: its own routes are reached through this."""

    def effective_route_contexts(self) -> Iterator[Any]: ...


def paths_of(app: FastAPI) -> set[str]:
    out: set[str] = set()
    for route in app.routes:
        if isinstance(route, _Included):
            out |= {str(r.path) for r in route.effective_route_contexts()}
        else:
            out.add(str(getattr(route, "path")))
    return out


@pytest.fixture
def page_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A bundle and an assets volume, as the image and the pod have them, so every mount exists."""
    client = tmp_path / "client"
    client.mkdir()
    (client / "game.js").write_text("// js")
    (client / "game.css").write_text("/* css */")
    assets = tmp_path / "assets" / "art"
    assets.mkdir(parents=True)
    (assets / "ruin.png").write_bytes(b"\x89PNG")
    monkeypatch.setattr(page, "CLIENT", client)
    monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "assets"))
    monkeypatch.setenv("BUILD_VERSION", "main-abc-1")
    return tmp_path


Imports = tuple[dict[str, set[str]], dict[str, set[str]]]


@pytest.fixture(scope="module")
def imports() -> Imports:
    """test_boundaries' graph of the package's units, and each unit's top-level names imported from outside the package:
    every file parsed once for the module."""
    outside: dict[str, set[str]] = {}
    for p in boundaries.PKG.rglob("*.py"):
        if p.parent != boundaries.PKG or p.name != "__init__.py":
            names = outside.setdefault(boundaries.top(p), set())
            for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
                if isinstance(n, ast.Import):
                    names |= {a.name.split(".")[0] for a in n.names}
                elif isinstance(n, ast.ImportFrom) and not n.level and n.module:
                    names.add(n.module.split(".")[0])
    return boundaries.edges(), outside


def reach(imports: Imports, start: str) -> tuple[set[str], set[str]]:
    """The package's units `start` imports, at any depth and lazily too, and the top-level names of everything outside
    the package those units' files import."""
    graph, outside_of = imports
    seen, todo = set[str](), [start]
    while todo:
        unit = todo.pop()
        if unit not in seen:
            seen.add(unit)
            todo += graph.get(unit, set())
    return seen, set[str]().union(*(outside_of.get(u, set[str]()) for u in seen))


def test_the_web_server_imports_nothing_that_needs_the_database_or_a_secret(imports: Imports):
    units, outside = reach(imports, "web")
    assert units <= ALLOWED, sorted(units - ALLOWED)
    assert outside & NEVER == set()
    app_units, app_outside = reach(imports, "main")   # the same probe sees them from the app, so it is not blind
    assert {"db", "api", "opening"} <= app_units and {"psycopg", "sqlalchemy"} <= app_outside


def test_every_route_of_the_app_is_a_server_path_or_a_file_the_web_pods_serve(page_files: Path):
    app_paths = paths_of(main.create_app())
    web_paths = paths_of(web.create_app())
    assert {"/api/saves/{save_id}/decisions", "/api/client-errors", "/build/main-abc-1", "/assets"} <= app_paths, "routes not found"
    assert sorted(p for p in app_paths if not web.is_server_path(p)) == sorted(web_paths - {"/webz"})   # /webz: the web pods' probe
    assert [p for p in web_paths if web.is_server_path(p)] == []
    for prefix in web.SERVER_PREFIXES:
        assert any(p.startswith(prefix) for p in app_paths), f"{prefix} routes nothing to the app: take it out"
    for exact in web.SERVER_EXACT:
        assert exact in app_paths, f"{exact} is not a route of the app"
    assert web.is_server_path("/api/saves") and not web.is_server_path("/apiary.png")
    assert not web.is_server_path("/healthz/x") and not web.is_server_path("/build/main-abc-1/game.js")


def test_the_web_server_serves_the_page_its_bundle_and_the_assets(page_files: Path):
    client = TestClient(web.create_app())
    front = client.get("/")
    assert front.status_code == 200 and '"/build/main-abc-1/game.js"' in front.text
    for path in ["/build/main-abc-1/game.js", "/build/main-abc-1/game.css",
                 "/icons/favicon.svg", "/favicon.ico", "/fonts/im-fell-english-sc-latin.woff2", "/fonts/fonts.css", "/privacy", "/robots.txt", "/llms.txt", "/assets/art/ruin.png"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert r.headers["x-ashfall-build"] == "main-abc-1", path
        assert r.headers.get_list("x-ashfall-server") == ["web"], path
    assert client.get("/assets/art/ruin.png").headers["content-type"] == "image/png"
    for path in ["/api/content", "/healthz", "/page-config.json", "/changes", "/openapi.json"]:
        r = client.get(path)
        assert r.status_code == 404, path
        assert r.headers["x-ashfall-build"] == "main-abc-1", path
        assert r.headers.get_list("x-ashfall-server") == ["web"], path


def test_webz_is_ready_when_the_images_bundle_is_there(page_files: Path):
    r = TestClient(web.create_app()).get("/webz")
    assert r.status_code == 200
    assert r.headers["x-ashfall-build"] == "main-abc-1"


@pytest.mark.parametrize("name", ["game.js", "game.css"])
def test_webz_fails_when_a_bundle_file_is_missing_or_empty(page_files: Path, name: str):
    client = TestClient(web.create_app())
    (page_files / "client" / name).write_text("")
    assert client.get("/webz").status_code == 503
    (page_files / "client" / name).unlink()
    assert client.get("/webz").status_code == 503


def test_webz_fails_in_an_image_with_no_bundle_directory(page_files: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(page, "CLIENT", page_files / "absent")
    assert TestClient(web.create_app()).get("/webz").status_code == 503


def test_webz_never_touches_the_assets_volume(page_files: Path):
    """A stalled CephFS must not unready the pods: the answer comes from the image alone."""
    client = TestClient(web.create_app())
    assets = page_files / "assets"
    (assets / "art" / "ruin.png").unlink()
    (assets / "art").rmdir()
    assets.rmdir()   # the volume is gone; /webz still answers
    assert client.get("/webz").status_code == 200


HEAD_FILES = ["/", "/favicon.ico", "/icons/favicon.svg", "/build/main-abc-1/game.js",
              "/assets/art/ruin.png", "/assets/art/missing.png"]


def assert_head_as_get(app: FastAPI, paths: list[str]) -> None:
    client = TestClient(app)
    for path in paths:
        got, head = client.get(path), client.head(path)
        assert (head.status_code, dict(head.headers)) == (got.status_code, dict(got.headers)), path
        assert head.content == b"" and (got.content != b"" or got.status_code == 404), path


def test_head_answers_every_page_and_file_as_get_does_without_a_body(page_files: Path):
    """A site that embeds the game checks its link with HEAD first (head.py)."""
    assert_head_as_get(web.create_app(), HEAD_FILES)
    game = main.create_app()   # built once: it compiles every shipped chapter's rules
    assert_head_as_get(game, [*HEAD_FILES, "/healthz", "/changes", "/page-config.json"])
    write = TestClient(game).head("/api/saves/1/advance")
    assert write.status_code == 405 and "POST" in write.headers["allow"]


def test_head_answers_the_content_as_get_does_without_a_body(page_files: Path):
    """/api/content, which serves every shipped chapter, has its own test: its GET and HEAD each build it."""
    assert_head_as_get(main.create_app(), ["/api/content"])


def test_the_web_pods_serve_the_worker_and_the_manifest_revalidated(page_files: Path):
    client = TestClient(web.create_app())
    sw = client.get("/sw.js")
    assert sw.status_code == 200 and sw.headers["content-type"].startswith("text/javascript")
    assert sw.headers["cache-control"] == "no-cache"
    assert '"push"' in sw.text and '"notificationclick"' in sw.text
    assert '"fetch"' not in sw.text, "a fetch handler would let a page run another build's bundle"
    m = client.get("/manifest.webmanifest")
    assert m.status_code == 200 and m.headers["content-type"].startswith("application/manifest+json")
    found = json.loads(m.text)
    assert found["display"] == "standalone" and found["start_url"] == "/"
    for icon in found["icons"]:
        assert client.get(icon["src"]).status_code == 200, icon
    assert '<link rel="manifest" href="/manifest.webmanifest">' in client.get("/").text
