"""The game's old name, answered with a permanent redirect to the new host, on every path of both servers (the app,
main.py, and the web pods, web/app.py): the edge sends the old host to both tiers. Only a Host that is exactly an old
name redirects, so probes that call by pod IP, and any request with no Host, pass. The old names come from
ASHFALL_OLD_HOSTS (comma separated)."""

import os
from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

NEW_ORIGIN = "https://ostmere.yggdrasil.pub"
DEFAULT_OLD_HOSTS = "ashfall.yggdrasil.pub"


def old_hosts(env: Mapping[str, str]) -> frozenset[str]:
    raw = env.get("ASHFALL_OLD_HOSTS") or DEFAULT_OLD_HOSTS
    return frozenset(h.strip().lower() for h in raw.split(",") if h.strip())


class OldHostRedirect:
    def __init__(self, app: Any, hosts: frozenset[str] | None = None) -> None:
        self.app = app
        self.hosts = old_hosts(os.environ) if hosts is None else hosts

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or self._host(scope) not in self.hosts:
            await self.app(scope, receive, send)
            return
        target = NEW_ORIGIN + (scope.get("raw_path") or quote(scope["path"]).encode()).decode("latin-1")
        if scope.get("query_string"):
            target += "?" + scope["query_string"].decode("latin-1")
        await send({"type": "http.response.start", "status": 301,
                    "headers": [(b"location", target.encode("latin-1")), (b"content-length", b"0")]})
        await send({"type": "http.response.body", "body": b""})

    @staticmethod
    def _host(scope: Any) -> str:
        for name, value in scope.get("headers", []):
            if name == b"host":
                return str(value.decode("latin-1").lower())
        return ""
