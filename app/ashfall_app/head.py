"""HEAD answered as GET, on every path of both servers (the app, main.py, and the web pods, web/app.py): the same
status and headers, no body. FastAPI's routes answer only the methods they declare, so without this a HEAD of `/` or
/healthz is a 405, and a site that checks a link with HEAD before embedding it refuses the game."""

from typing import Any


class HeadAsGet:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or scope["method"] != "HEAD":
            await self.app(scope, receive, send)
            return

        async def bodiless(message: Any) -> None:
            if message["type"] == "http.response.body":
                message = {**message, "body": b""}
            await send(message)

        await self.app({**scope, "method": "GET"}, receive, bodiless)
