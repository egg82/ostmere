"""A request that meets a failover runs again, once, when that cannot apply it twice (db/failover.py); otherwise, or when
the second run meets one too, it is answered 503 save_unavailable with Retry-After and changes nothing the client can
rely on. The second run takes a new checkout (db/unit.py), and the connection that failed is not lent again: the pool's
check (db/writable.py) refuses a read-only one, and a dropped one never goes back. The request body is read once and
kept, so a second run sees what the first did."""
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from starlette.concurrency import run_in_threadpool

from .. import logs
from ..db import failover, unit
from .errors import unavailable

log = logging.getLogger("ashfall.db")
Handler = Callable[[Request], Coroutine[Any, Any, Response]]
MESSAGE = "the database is switching over: ask again shortly"


class _Replay(Exception):
    """The first run met a failover that is safe to run again."""


async def once(handler: Handler, request: Request) -> Response:
    """`handler`'s answer; its errors, a failover aside, as they are."""
    try:
        return await _attempt(handler, request, may_replay=True)
    except _Replay:
        return await _attempt(handler, request, may_replay=False)


async def _attempt(handler: Handler, request: Request, may_replay: bool) -> Response:
    attempt = failover.start_attempt()
    started = time.perf_counter()
    try:
        return await _settled(handler, request)
    except Exception as ex:
        failure = failover.classify(ex)
        if failure is None:
            raise
        unit.discard()
        replay = may_replay and failover.replayable(attempt, failure)
        logs.warning(log, "db.failover", kind=failure.kind, sqlstate=failure.sqlstate, replayed=replay,
                     ms=int((time.perf_counter() - started) * 1000))
        if replay:
            raise _Replay from ex
        raise unavailable(MESSAGE) from ex


async def _settled(handler: Handler, request: Request) -> Response:
    """`handler`'s answer or error, with the reads its unit still holds open committed after it (db/unit.py)."""
    try:
        response = await handler(request)
    except Exception as ex:
        if failover.classify(ex) is None:
            await run_in_threadpool(unit.settle)
        raise
    await run_in_threadpool(unit.settle)
    return response
