"""The page's files: the shell (static/index.html), the privacy page, robots.txt and llms.txt, its bundle, the icons, the
fonts and the assets volume. Served the same way by the web pods (web/app.py) and by the app itself (main.py), so a run
with no web pods still has a page."""

import hashlib
import mimetypes
import os
from pathlib import Path
from urllib.parse import parse_qs

import anyio
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope

from . import og

HERE = Path(__file__).parent.parent
ICONS = HERE / "static" / "icons"
FONTS = HERE / "static" / "fonts"
FONTS_LINK = '<link rel="stylesheet" href="/fonts/fonts.css">'


def inline_fonts(html: str) -> str:
    """The page with its fonts.css link replaced by the file's rules, whose font files are named from /fonts/: the
    stylesheet is neither a request that blocks the first paint nor one revalidated on every load."""
    css = (FONTS / "fonts.css").read_text().replace("url(", "url(/fonts/")
    assert FONTS_LINK in html, "a page whose fonts are not linked"
    return html.replace(FONTS_LINK, f"<style>\n{css}</style>")


INDEX = inline_fonts((HERE / "static" / "index.html").read_text())   # {{build}}: the build of the bundle it loads
PRIVACY = inline_fonts((HERE / "static" / "privacy.html").read_text())
ROBOTS = (HERE / "static" / "robots.txt").read_text()
PUSH = HERE / "static" / "push"   # the service worker and web manifest, served from the root (reminders)
LLMS = (HERE / "static" / "llms.txt").read_text()
CLIENT = HERE / "build" / "client"   # the bundled game (app/client/), copied in by the Containerfile; absent locally

GZIP_MIN = 1024   # bytes: a smaller answer is sent as it is, by both servers (main.py, web/app.py)

mimetypes.add_type("font/woff2", ".woff2")   # the platform table of some images has no font types

ASSET_TYPES = {
    ".png": "image/png",
    ".webp": "image/webp",
    ".ogg": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".wav": "audio/wav",
    ".json": "application/json",
}


class RevalidatedFiles(StaticFiles):
    """Files replaced under the same names (a deploy, a reseed): the browser keeps its copy but revalidates it by ETag
    each time (a 304 when unchanged), never a blind or heuristic long cache."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code in (200, 304):
            response.headers["Cache-Control"] = "public, no-cache"
        return response


class BuildFiles(StaticFiles):
    """The bundle, at a path naming its build: the files under it never change, so a browser keeps them for good."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code in (200, 304):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


HASH_LENGTH = 12   # hex digits of a file's sha256 in a scene layer's `?h=` (tools/scene/build.py)


class AssetFiles(RevalidatedFiles):
    """The assets volume, read-only, with fixed content types. A file asked for by its own content hash (`?h=`) never
    changes under that URL, so it is kept for good; the volume is reseeded by hand with no atomic swap, so the hash is
    checked against the file served, never trusted: the answer carries the one open file's bytes that were hashed."""

    def __init__(self, *, directory: Path) -> None:
        super().__init__(directory=directory)
        self.hashes: dict[str, tuple[int, int, str]] = {}   # path -> (mtime_ns, size, hash prefix)

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            content_type = ASSET_TYPES.get(Path(path).suffix.lower())
            if content_type:
                response.headers["Content-Type"] = content_type
            body = await anyio.to_thread.run_sync(self.body_if_asked_by_hash, path, scope)
            if body is not None:
                headers = {k: v for k, v in response.headers.items() if k != "content-length"}
                headers["cache-control"] = "public, max-age=31536000, immutable"
                return Response(body, headers=headers)
        elif response.status_code == 304 and await anyio.to_thread.run_sync(self.asked_by_hash, path, scope):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    def asked_hash(self, scope: Scope) -> str:
        return parse_qs(scope["query_string"].decode("latin-1")).get("h", [""])[0]

    def kept_hash(self, full: str, stat: os.stat_result, body: bytes | None) -> str:
        """The hash prefix of the file `stat` describes; `body` is its bytes when the caller already holds them."""
        kept = self.hashes.get(full)
        if kept is None or kept[:2] != (stat.st_mtime_ns, stat.st_size):
            if body is None:
                body = Path(full).read_bytes()
            kept = (stat.st_mtime_ns, stat.st_size, hashlib.sha256(body).hexdigest()[:HASH_LENGTH])
            self.hashes[full] = kept
        return kept[2]

    def card_hash(self, path: str) -> str | None:
        """The hash prefix of the file at `path`, None when the volume has none there."""
        full, stat = self.lookup_path(path)
        return self.kept_hash(full, stat, None) if stat is not None else None

    def asked_by_hash(self, path: str, scope: Scope) -> bool:
        """For a 304, which sends no body: the file's hash is the asked one."""
        asked = self.asked_hash(scope)
        full, stat = self.lookup_path(path)
        return bool(asked) and stat is not None and asked == self.kept_hash(full, stat, None)

    def body_if_asked_by_hash(self, path: str, scope: Scope) -> bytes | None:
        """The file's bytes when they hash to the asked `?h=`: stat and bytes come from one open file."""
        if not self.asked_hash(scope):
            return None
        full, stat = self.lookup_path(path)
        if stat is None:
            return None
        with open(full, "rb") as handle:
            opened = os.fstat(handle.fileno())
            body = handle.read()
        return body if self.asked_hash(scope) == self.kept_hash(full, opened, body) else None


def bundle_present() -> bool:
    """The bundle's files are in the image and not empty."""
    return all((CLIENT / name).is_file() and (CLIENT / name).stat().st_size > 0 for name in ("game.js", "game.css"))


def serve_bundle(app: FastAPI, version: str) -> None:
    if CLIENT.is_dir():
        # The bundle at a path naming its build, so a page from one build never runs another's bundle mid-deploy (a 404
        # there reloads the page once: static/index.html).
        app.mount(f"/build/{version}", BuildFiles(directory=CLIENT), name="client")


def serve_shell(app: FastAPI, version: str) -> None:
    front = INDEX.replace("{{build}}", version)

    # Generated by tools/favicon.py; browsers ask for /favicon.ico unprompted, the page links the rest.
    app.mount("/icons", RevalidatedFiles(directory=ICONS), name="icons")
    app.mount("/fonts", RevalidatedFiles(directory=FONTS), name="fonts")

    # At the root, so the worker's scope is the whole site; revalidated, so a new build's worker is picked up.
    @app.get("/sw.js", include_in_schema=False)
    def service_worker() -> FileResponse:
        return FileResponse(PUSH / "sw.js", media_type="text/javascript", headers={"Cache-Control": "no-cache"})

    @app.get("/manifest.webmanifest", include_in_schema=False)
    def manifest() -> FileResponse:
        return FileResponse(PUSH / "manifest.webmanifest", media_type="application/manifest+json",
                            headers={"Cache-Control": "public, no-cache"})

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        return FileResponse(ICONS / "favicon.ico", media_type="image/x-icon", headers={"Cache-Control": "public, no-cache"})

    assets = Path(os.environ.get("ASSETS_DIR", "/assets"))
    files = AssetFiles(directory=assets) if assets.is_dir() else None

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        return front.replace(og.IMAGE_PLACEHOLDER, og.card_url(files.card_hash(og.CARD_PATH) if files else None))

    @app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
    def privacy() -> str:
        return PRIVACY

    @app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
    def robots() -> str:
        return ROBOTS

    @app.get("/llms.txt", response_class=PlainTextResponse, include_in_schema=False)
    def llms() -> str:
        return LLMS

    # Licensed and generated assets live on the pods' read-only volume, never in the image or git (docs/engineering.md);
    # without it /assets/* is a plain 404 and the server still starts.
    if files:
        app.mount("/assets", files, name="assets")
