"""Writes only from this site, with JSON bodies (habits' signin/csrf.py), for every POST, PUT, PATCH and DELETE
under /api/. The session cookie is SameSite=None (cookies.py), so it rides on requests other sites make: this check
alone keeps their writes out.

- An `Origin` must be https and name the host the request came to (the gateway and the tunnel keep the Host the
  browser sent). The site is served only over https, so a page on its host over plain http is a network attacker's.
  With no Origin, `Sec-Fetch-Site` must say same-origin or none. A write with neither header is refused: every browser
  sends one of them, and a write that proves nothing about where it came from changes nothing.
- A body must be JSON. A plain cross-site form can only send form or text bodies, never application/json.

Refusals are the API's error body (api/CONTRACT.txt): 403 cross_site, 415 not_json, never cached."""

import json
from typing import Any
from urllib.parse import urlsplit

WRITES = {"POST", "PUT", "PATCH", "DELETE"}
PREFIX = "/api/"


def origin_ok(headers: dict[str, str]) -> bool:
    origin = headers.get("origin")
    if origin is not None:
        parts = urlsplit(origin)
        return parts.scheme == "https" and bool(parts.netloc) and parts.netloc.lower() == headers.get("host", "").lower()
    return headers.get("sec-fetch-site") in ("same-origin", "none")


def body_ok(headers: dict[str, str]) -> bool:
    has_body = headers.get("content-length", "0") not in ("", "0") or "transfer-encoding" in headers
    ctype = headers.get("content-type")
    if ctype is None:
        return not has_body
    return ctype.split(";")[0].strip().lower() == "application/json"


class CsrfMiddleware:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] == "http" and scope["method"] in WRITES and str(scope["path"]).startswith(PREFIX):
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope["headers"]}
            if not origin_ok(headers):
                await refuse(send, 403, "cross_site", "a write from another site: nothing was changed")
                return
            if not body_ok(headers):
                await refuse(send, 415, "not_json", "a write's body must be application/json")
                return
        await self.app(scope, receive, send)


async def refuse(send: Any, status: int, code: str, message: str) -> None:
    body = json.dumps({"code": code, "message": message, "step": None}).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()),
                            (b"cache-control", b"no-store")]})
    await send({"type": "http.response.body", "body": body})
