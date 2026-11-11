"""The API's route class: every answer goes through it. FastAPI's own `{"detail": ...}` body is not the contract
(CONTRACT.txt), so a GameError becomes its ApiError body and status, and a request the models reject (an unknown
field, a share past 100%) is a decision that does not fit: invalid_decision. A write (POST, PUT) that succeeded renews
its session (session.py), so a refused request writes nothing. A request runs on one pool checkout (db/unit.py). A
database failover under a request is replayed or answered 503 (replay.py). Every answer is logged once
(requestlog.py)."""
import time
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from ..db import unit
from . import replay, requestlog, session
from .device_routes import NO_STORE
from .error_models import ErrorCode
from .errors import GameError, invalid_decision


class ErrorRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()
        template = self.path

        async def guarded(request: Request) -> Response:
            with unit.scope():
                return await answered(request)

        async def answered(request: Request) -> Response:
            started = time.perf_counter()
            code: ErrorCode | None = None
            try:
                response = await replay.once(handler, request)
            except GameError as ex:
                code, response = ex.body.code, _answer(ex)
            except RequestValidationError as ex:
                where = "; ".join(f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in ex.errors())
                code, response = ErrorCode.INVALID_DECISION, _answer(invalid_decision(f"the request does not fit the models: {where}"))
            if response.status_code < 400 and request.method in ("POST", "PUT"):
                await session.renew(request)
            if template in NO_STORE:
                response.headers["Cache-Control"] = "no-store"
            requestlog.record(template, request.path_params.get("save_id"), await request.body(),
                              response.status_code, int((time.perf_counter() - started) * 1000), code,
                              request.headers, bytes(response.body))
            return response

        return guarded


def _answer(ex: GameError) -> Response:
    return JSONResponse(status_code=ex.status, content=ex.body.model_dump(mode="json"), headers=ex.headers)
