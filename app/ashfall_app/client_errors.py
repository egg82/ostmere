"""Bugs friends hit in the browser, as one logfmt line each (event=client_error) so they reach Loki. The page posts
{kind, message, source, version, route, decision, since_begin_s}, or for kind=leave the totals when the
page was left (event=game_leave: since_begin_s, game_time, last_project, decisions, reached_end); the server logs exactly those, message and source cut
to 300 characters. Never the state string, the client address or player content. A burst past RATE reports a minute is
dropped (the page also caps itself at 10 per load). Outside the game API's contract: not in openapi.json."""
import logging
import time
from collections import deque
from collections.abc import Callable
from enum import StrEnum

from fastapi import APIRouter, Response
from pydantic import BaseModel

from . import logs

CUT = 300
RATE = 30   # reports a minute, across all pages, per pod (RateLimit)
_log = logging.getLogger("ashfall.client")


class ClientErrorKind(StrEnum):
    ERROR = "error"
    REJECTION = "rejection"
    REQUEST = "request"
    LEAVE = "leave"


class ClientError(BaseModel):
    kind: ClientErrorKind
    message: str = ""
    source: str = ""
    version: str = ""
    route: str | None = None
    decision: str | None = None
    since_begin_s: int | None = None
    game_time: int | None = None   # leave only: the game clock when the player went away
    last_project: str | None = None   # leave only: the last one-off project completed
    decisions: int | None = None   # leave only
    reached_end: int | None = None   # leave only: 0/1


class RateLimit:
    """At most `limit` passes in any `window` seconds; the clock is injected. Held in process memory, so each pod
    keeps its own: by design, since it guards the log from a flood, not a trust boundary (n pods let n times RATE
    through)."""

    def __init__(self, limit: int, window: float, clock: Callable[[], float] = time.monotonic) -> None:
        self._limit, self._window, self._clock = limit, window, clock
        self._seen: deque[float] = deque()

    def allow(self) -> bool:
        now = self._clock()
        while self._seen and now - self._seen[0] >= self._window:
            self._seen.popleft()
        if len(self._seen) >= self._limit:
            return False
        self._seen.append(now)
        return True


def log_client_error(report: ClientError) -> None:
    if report.kind is ClientErrorKind.LEAVE:
        logs.info(
            _log, "game_leave", since_begin_s=report.since_begin_s, game_time=report.game_time,
            last_project=_cut(report.last_project), decisions=report.decisions, reached_end=report.reached_end,
            version=_cut(report.version))
        return
    logs.warning(
        _log, "client_error", kind=report.kind.value, message=report.message[:CUT], source=report.source[:CUT],
        version=_cut(report.version), route=_cut(report.route), decision=_cut(report.decision),
        since_begin_s=report.since_begin_s)


def _cut(value: str | None) -> str | None:
    return (value or "")[:CUT] or None


def routes(limit: RateLimit | None = None) -> APIRouter:
    router = APIRouter()
    gate = limit or RateLimit(RATE, 60.0)

    @router.post("/api/client-errors", status_code=204, include_in_schema=False)
    def post_client_error(report: ClientError) -> Response:
        if gate.allow():
            log_client_error(report)
        return Response(status_code=204)

    return router
