"""A request body over MAX_BODY_BYTES under /api/ is refused before any route parses it: 413 too_large
(api/CONTRACT.txt, ERRORS), by the declared Content-Length when there is one, else by the bytes counted as they
arrive (a chunked body has no length). The refusal is logged by route and size only."""
import logging
from typing import Any

from .. import logs
from .csrf import PREFIX, refuse

MAX_BODY_BYTES = 256 * 1024
_log = logging.getLogger("ashfall.app")
_ROUTE_CUT = 80


def declared(headers: list[tuple[bytes, bytes]]) -> int | None:
    for name, value in headers:
        if name == b"content-length" and value.isdigit():
            return int(value)
    return None


class BodyLimit:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or not str(scope["path"]).startswith(PREFIX):
            await self.app(scope, receive, send)
            return
        size = declared(scope["headers"])
        if size is not None and size > MAX_BODY_BYTES:
            await self._refused(scope, send, size)
            return
        seen = 0
        over = False

        async def counted() -> Any:
            nonlocal seen, over
            message = await receive()
            if message["type"] == "http.request":
                seen += len(message.get("body", b""))
                if seen > MAX_BODY_BYTES:
                    over = True
                    return {"type": "http.disconnect"}
            return message

        async def quiet(message: Any) -> None:
            if not over:
                await send(message)

        try:
            await self.app(scope, counted, quiet)
        except Exception:
            if not over:
                raise
        if over:
            await self._refused(scope, send, seen)

    async def _refused(self, scope: Any, send: Any, size: int) -> None:
        logs.info(_log, "api.too_large", route=str(scope["path"])[:_ROUTE_CUT], bytes=size)
        await refuse(send, 413, "too_large", f"a request body may not pass {MAX_BODY_BYTES} bytes")
