"""Names the build that answered on every response, errors included (api/CONTRACT.txt): while a deploy rolls, two
builds serve at once, and a reply is only read right knowing which one sent it. Both servers use it, the app (main.py)
and the web pods (web/app.py), and each names itself in X-Ashfall-Server, so a check of the edge's routing can say
which Service answered a path."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.responses import Response

BUILD_HEADER = "X-Ashfall-Build"
SERVER_HEADER = "X-Ashfall-Server"


class BuildHeader:
    def __init__(self, app: Any, build: str, server: str) -> None:
        self.app = app
        self._headers = [(BUILD_HEADER.lower().encode(), build.encode()), (SERVER_HEADER.lower().encode(), server.encode())]

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def named(message: Any) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), *self._headers]
            await send(message)

        await self.app(scope, receive, named)


def name_every_answer(app: FastAPI, version: str, server: str) -> None:
    app.add_middleware(BuildHeader, build=version, server=server)

    # An unhandled error is answered outside every middleware (Starlette's ServerErrorMiddleware): this answer is the
    # same plain 500, named like the rest.
    @app.exception_handler(Exception)
    def server_error(_: Request, __: Exception) -> Response:
        return PlainTextResponse("Internal Server Error", status_code=500, headers={BUILD_HEADER: version, SERVER_HEADER: server})
