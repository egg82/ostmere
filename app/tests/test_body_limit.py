"""A request body over the limit is refused before it is parsed (api/CONTRACT.txt, ERRORS: 413 too_large), by its
declared length or, for a streamed body, by the bytes counted as they arrive; the refusal is logged by route and size
only."""
import asyncio
import json
from importlib import import_module
from typing import Any

import pytest
from fastapi.testclient import TestClient

from ashfall_app.main import create_app

LIMIT = 256 * 1024
JSON_HEADERS = {"Origin": "https://testserver", "Content-Type": "application/json"}


def report(size: int) -> bytes:
    pad = size - len(b'{"kind":"error","message":""}')
    return b'{"kind":"error","message":"' + b"x" * pad + b'"}'


def test_a_body_at_the_limit_is_taken():
    client = TestClient(create_app(), headers=JSON_HEADERS)
    assert client.post("/api/client-errors", content=report(LIMIT)).status_code == 204


def test_a_declared_length_over_the_limit_is_refused_as_too_large():
    client = TestClient(create_app(), headers=JSON_HEADERS)
    r = client.post("/api/client-errors", content=report(LIMIT + 1))
    assert r.status_code == 413
    assert r.json()["code"] == "too_large"


def test_the_account_less_routes_are_covered_too():
    client = TestClient(create_app(), headers=JSON_HEADERS)
    assert client.post("/api/join", content=report(LIMIT + 1)).status_code == 413


def test_a_refusal_is_logged_by_route_and_size_only(capsys: pytest.CaptureFixture[str]):
    client = TestClient(create_app(), headers=JSON_HEADERS)
    capsys.readouterr()
    client.post("/api/client-errors", content=report(LIMIT + 1))
    (line,) = [ln for ln in capsys.readouterr().out.splitlines() if "event=api.too_large" in ln]
    assert "route=/api/client-errors" in line and f"bytes={LIMIT + 1}" in line and "xxxx" not in line


async def streamed(chunks: list[bytes]) -> tuple[list[dict[str, Any]], int]:
    """The body arriving in `chunks` with no Content-Length, through the middleware in front of an app that reads it
    all and answers 204; the messages sent, and how many chunks the app was given."""
    BodyLimit = import_module("ashfall_app.accounts.body_limit").BodyLimit
    taken = 0
    sent: list[dict[str, Any]] = []
    queue = [{"type": "http.request", "body": c, "more_body": True} for c in chunks]
    queue.append({"type": "http.request", "body": b"", "more_body": False})

    async def receive() -> dict[str, Any]:
        return queue.pop(0) if queue else {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    async def app(scope: Any, recv: Any, snd: Any) -> None:
        nonlocal taken
        while True:
            message = await recv()
            if message["type"] != "http.request":
                break
            taken += 1
            if not message.get("more_body"):
                break
        await snd({"type": "http.response.start", "status": 204, "headers": []})
        await snd({"type": "http.response.body", "body": b""})

    scope: dict[str, Any] = {"type": "http", "method": "POST", "path": "/api/client-errors", "headers": []}
    await BodyLimit(app)(scope, receive, send)
    return sent, taken


def test_a_streamed_body_over_the_limit_is_refused_and_not_read_on():
    sent, taken = asyncio.run(streamed([b"x" * 100_000] * 4))
    assert sent[0]["status"] == 413 and json.loads(sent[1]["body"])["code"] == "too_large"
    assert taken < 4
    assert len([m for m in sent if m["type"] == "http.response.start"]) == 1


def test_a_streamed_body_under_the_limit_passes():
    sent, _ = asyncio.run(streamed([b"x" * 100_000] * 2))
    assert sent[0]["status"] == 204
