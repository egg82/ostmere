"""The game API's routes, all under /api: the content, the account and save endpoints (save_routes.py), an account's
games (games_routes.py), moving an account to another device (device_routes.py) and reminders (reminder_routes.py).

Contract for the client author: CONTRACT.txt beside this file. Errors are errors.py; every route answers through its
route class, so each request is logged once and every error is an ApiError."""
from fastapi import APIRouter, Request, Response

from .route import ErrorRoute
from .content_models import Content
from .device_routes import add_device_routes
from .games_routes import add_games_routes
from .reminder_routes import add_reminder_routes
from .save_routes import add_save_routes
from .service import Game

PUBLIC_URL = "https://ostmere.yggdrasil.pub"


def routes(game: Game, public_url: str = PUBLIC_URL) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["game"], route_class=ErrorRoute)

    @router.get("/content", response_model=Content, operation_id="get_content")
    def get_content(request: Request, response: Response) -> Content | Response:
        """Static: text, labels, cards and scales for the opening. Fetch once; rules_digest names the rules. ETag names
        the build and the rules: If-None-Match with it is a 304."""
        headers = {"ETag": game.content_tag, "Cache-Control": "no-cache"}
        sent = [t.strip() for t in request.headers.get("if-none-match", "").split(",")]
        if game.content_tag in sent or "*" in sent:
            return Response(status_code=304, headers=headers)
        response.headers.update(headers)
        return game.content()

    add_save_routes(router, game)
    add_games_routes(router, game)
    add_device_routes(router, public_url)
    add_reminder_routes(router)
    return router
