"""AssetFiles (ashfall_app/web/page.py): an answer marked immutable for `?h=` carries the bytes that hash to it."""

import asyncio
import hashlib
from collections.abc import Callable, MutableMapping
from pathlib import Path
from typing import Any

from ashfall_app.web.page import HASH_LENGTH, AssetFiles

Message = MutableMapping[str, Any]


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()[:HASH_LENGTH]


async def fetch(files: AssetFiles, query: str, between: Callable[[], None] = lambda: None) -> tuple[dict[str, str], bytes]:
    """Ask for art/a.png, run `between` after the headers are decided and before the body goes out, return both."""
    scope: Message = {"type": "http", "method": "GET", "path": "/art/a.png", "query_string": query.encode(), "headers": []}
    response = await files.get_response("art/a.png", scope)
    between()
    sent: list[Message] = []

    async def receive() -> Message:
        await asyncio.Event().wait()   # no client disconnect
        return {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        sent.append(message)

    await response(scope, receive, send)
    names = [k.decode().lower() for k, _ in sent[0]["headers"]]
    assert len(names) == len(set(names)), names   # one Cache-Control, not two
    headers = {k.decode().lower(): v.decode() for k, v in sent[0]["headers"]}
    return headers, b"".join(m.get("body", b"") for m in sent[1:])


def volume(tmp_path: Path, body: bytes) -> tuple[AssetFiles, Path]:
    target = tmp_path / "art" / "a.png"
    target.parent.mkdir()
    target.write_bytes(body)
    return AssetFiles(directory=tmp_path), target


def reseed(target: Path, body: bytes) -> None:
    """What the seed job does: a new file renamed over the old one."""
    staged = target.with_name("staged")
    staged.write_bytes(body)
    staged.replace(target)


def test_an_asset_asked_by_its_hash_is_immutable_and_sent_whole(tmp_path: Path):
    body = b"\x89PNG" + b"a" * 5000
    files, _ = volume(tmp_path, body)
    headers, sent = asyncio.run(fetch(files, f"h={digest(body)}"))
    assert headers["cache-control"] == "public, max-age=31536000, immutable"
    assert sent == body and headers["content-length"] == str(len(body)) and headers["content-type"] == "image/png"


def test_an_asset_asked_by_another_hash_or_none_is_revalidated(tmp_path: Path):
    files, _ = volume(tmp_path, b"abc")
    for query in ("h=000000000000", ""):
        headers, sent = asyncio.run(fetch(files, query))
        assert headers["cache-control"] == "public, no-cache" and sent == b"abc", query


def test_a_reseed_between_the_check_and_the_send_never_puts_other_bytes_under_the_hash(tmp_path: Path):
    old, new = b"old" * 2000, b"new" * 2000
    files, target = volume(tmp_path, old)
    headers, sent = asyncio.run(fetch(files, f"h={digest(old)}", between=lambda: reseed(target, new)))
    if headers["cache-control"].endswith("immutable"):
        assert digest(sent) == digest(old)
    assert sent in (old, new)
