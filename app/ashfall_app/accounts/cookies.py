"""Cookies set from anywhere in a request (a dependency, a route), added to whatever response goes out: a model, an
error, a file. A plain ASGI middleware, so nothing about the response has to cooperate. (habits' signin/cookies.py.)"""

from http.cookies import SimpleCookie
from typing import Any

from starlette.requests import HTTPConnection

KEY = "ashfall.cookies"
SESSION = "__Host-ashfall_session"   # __Host-: Secure, Path=/, no Domain, so no subdomain can set or read it


def queue(conn: HTTPConnection, name: str, value: str, max_age: int) -> None:
    """Sets `name` on this request's response: Secure, HttpOnly, SameSite=None, Partitioned, Path=/. None and
    Partitioned keep the game in a page that embeds it from another site (CHIPS: one cookie per top-level site, so the
    embedding site never sees this one's); writes are held to this site by csrf.py, not by SameSite."""
    c: SimpleCookie = SimpleCookie()
    c[name] = value
    m = c[name]
    m["path"], m["max-age"], m["secure"], m["httponly"], m["samesite"] = "/", str(max_age), True, True, "None"
    pending: dict[str, str] = conn.scope.setdefault(KEY, {})
    pending[name] = m.OutputString() + "; Partitioned"   # http.cookies knows the attribute only from Python 3.14


def clear(conn: HTTPConnection, name: str) -> None:
    """Ends `name` in the browser on this request's response."""
    queue(conn, name, "", 0)


def read(conn: HTTPConnection, name: str) -> str | None:
    """The value this request carries, or the one queued for it in this request."""
    pending: dict[str, str] = conn.scope.get(KEY, {})
    queued = pending.get(name)
    if queued is not None:
        value = SimpleCookie(queued.partition(";")[0]).get(name)
        return value.value if value is not None and value.value else None
    return conn.cookies.get(name) or None


class CookieMiddleware:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def sending(message: Any) -> None:
            if message["type"] == "http.response.start":
                pending: dict[str, str] = scope.get(KEY, {})
                extra = [(b"set-cookie", v.encode("latin-1")) for v in pending.values()]
                if extra:
                    message = {**message, "headers": [*message.get("headers", []), *extra]}
            await send(message)

        await self.app(scope, receive, sending)
