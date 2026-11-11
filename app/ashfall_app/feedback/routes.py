"""POST /api/feedback (api/CONTRACT.txt): the words a tester sends from the page. Open to a browser with no account
too (the limit then counts its client address). The text is never logged (service.py)."""
from typing import Annotated

from fastapi import APIRouter, Request, Response
from pydantic import StringConstraints

from ..accounts.interface import Limited
from ..api import session
from ..api.error_models import ApiError
from ..api.errors import rate_limited, unavailable
from ..api.limits import NO_NUL
from ..api.models import Request as WireRequest
from ..api.route import ErrorRoute
from ..api.saves_models import SaveId
from .service import PgFeedback

TEXT_MAX = 2000


class FeedbackRequest(WireRequest):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=TEXT_MAX, pattern=NO_NUL)]
    """What the player wrote; surrounding space is trimmed, and what is left is 1 to 2000 characters."""
    save_id: SaveId | None = None
    """The save they were playing; kept only when this browser's account owns it."""


def routes(feedback: PgFeedback | None) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["game"], route_class=ErrorRoute)

    @router.post("/feedback", status_code=204, operation_id="send_feedback", responses={
        422: {"model": ApiError, "description": "invalid_decision (an empty or too long text)"},
        429: {"model": ApiError, "description": "rate_limited"},
        503: {"model": ApiError, "description": "save_unavailable (Retry-After)"}})
    def send_feedback(request: Request, body: FeedbackRequest) -> Response:
        """Keeps a tester's words with the build and, if the save is theirs, where in the game they were."""
        found = session.who(request)
        if feedback is None:
            raise unavailable("no database")
        try:
            feedback.add(found, session.address(request), body.text, body.save_id)
        except Limited as ex:
            raise rate_limited("too much feedback just now: try again later") from ex
        return Response(status_code=204)

    return router
