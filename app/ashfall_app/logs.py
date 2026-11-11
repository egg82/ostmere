"""The one logging setup: one logfmt line per event to stdout, which Alloy ships to Loki. Copied from habits'
`logs.py` and typed.

    ts=2026-10-11T09:00:01.123Z level=info logger=ashfall.game event=game.request route=/api/content status=200 ms=4

Call sites say `logs.info(log, "app.start", rules=digest)`; a field is an id, a count, a kind, a duration or a status.
Never in a line: player content, the state string, client addresses, keys, tokens, cookies. An exception is written as
its type chain and frames, never its message. `tag()` stands in for a value that is only ever compared."""

import contextvars
import hashlib
import logging
import os
import re
import sys
import time
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from types import TracebackType
from typing import Any, final

_QUIET = ("urllib3", "httpx", "httpcore", "asyncio")   # their own lines carry URLs: warnings only
_MAX = 300
# The probes, not worth a line each: the app's, and the web pods'.
_BARE = ("/healthz", "/webz")


def tag(value: object) -> str:
    """A short stable stand-in for a value that must not be written (a state string): equal values, equal tags."""
    return hashlib.sha256(str(value).encode()).hexdigest()[:8]


_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_NAMED = {"\n": "\\n", "\r": "\\r", "\t": "\\t"}


def _escape(m: re.Match[str]) -> str:
    return _NAMED.get(m.group(), f"\\x{ord(m.group()):02x}")


def _val(v: object) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        v = round(v, 2)
    s = _CONTROL.sub(_escape, str(v).replace("\\", "\\\\").replace('"', '\\"'))
    if len(s) > _MAX:
        s = s[:_MAX] + "..."
    return f'"{s}"' if not s or any(ch in s for ch in ' ="\\') else s


def _frames(tb: TracebackType | None) -> str:
    out: list[str] = []
    for f in traceback.extract_tb(tb)[-12:]:
        name = f.filename.replace("\\", "/")
        name = name.split("ashfall_app/", 1)[1] if "ashfall_app/" in name else name.rsplit("/", 1)[-1]
        out.append(f"{name}:{f.lineno}:{f.name}")
    return ">".join(out)


def _chain(exc: BaseException | None) -> str:
    seen: set[int] = set()
    types: list[str] = []
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        types.append(type(exc).__name__)
        exc = exc.__cause__ or (None if exc.__suppress_context__ else exc.__context__)
    return "<".join(types)


class Logfmt(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(record.msecs):03d}Z"
        fields: dict[str, object] | None = getattr(record, "fields", None)
        parts: list[tuple[str, object]] = [("ts", ts), ("level", record.levelname.lower()), ("logger", record.name)]
        if fields is None:   # a library's own line: its message is all there is
            parts += [("event", "log"), ("msg", record.getMessage())]
        else:
            parts.append(("event", record.msg))
            parts += [(k, v) for k, v in fields.items() if v is not None]
        if record.exc_info and record.exc_info[1] is not None:
            parts += [("exc", _chain(record.exc_info[1])), ("tb", _frames(record.exc_info[2]))]
        return " ".join(f"{k}={_val(v)}" for k, v in parts)


@final
class _Stdout(logging.Handler):
    """stdout as it is when a line is written, not when the handler was made (a test swaps it)."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            sys.stdout.write(self.format(record) + "\n")
            sys.stdout.flush()
        except Exception:
            self.handleError(record)


_started: contextvars.ContextVar[float | None] = contextvars.ContextVar("request_started", default=None)


class RequestClock:
    """Starts the clock the access line reads: uvicorn writes that line from inside the app's own call, when the
    response is complete, so the time since this middleware took the request is the request's server time."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] == "http":
            _started.set(time.perf_counter())
        await self.app(scope, receive, send)


class Access(logging.Filter):
    """Uvicorn's access line as an event: method, path, status and ms, no client address; probes dropped; a query
    string never written."""

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if not isinstance(args, tuple) or len(args) != 5:
            return True
        _, method, target, _, status = args
        path = str(target).split("?", 1)[0]
        if path in _BARE:
            return False
        t0 = _started.get()
        ms = None if t0 is None else int((time.perf_counter() - t0) * 1000)
        record.msg, record.args = "http.request", None
        record.fields = {"method": method, "path": path, "status": status, "ms": ms}
        return True


def setup(env: Mapping[str, str] = os.environ) -> None:
    """Idempotent. Level from LOG_LEVEL (default info). Uvicorn's own loggers are pointed at the same handler."""
    level = getattr(logging, (env.get("LOG_LEVEL") or "info").strip().upper(), logging.INFO)
    if not isinstance(level, int):
        level = logging.INFO
    root = logging.getLogger()
    if not any(isinstance(h, _Stdout) for h in root.handlers):
        h = _Stdout()
        h.setFormatter(Logfmt())
        root.addHandler(h)
    root.setLevel(level)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
    access = logging.getLogger("uvicorn.access")
    if not any(isinstance(f, Access) for f in access.filters):
        access.addFilter(Access())
    for name in _QUIET:
        logging.getLogger(name).setLevel(max(level, logging.WARNING))


def emit(log: logging.Logger, level: int, event: str, **fields: object) -> None:
    if log.isEnabledFor(level):
        log.log(level, event, extra={"fields": fields})


def info(log: logging.Logger, event: str, **fields: object) -> None:
    emit(log, logging.INFO, event, **fields)


def warning(log: logging.Logger, event: str, **fields: object) -> None:
    emit(log, logging.WARNING, event, **fields)


def error(log: logging.Logger, event: str, **fields: object) -> None:
    emit(log, logging.ERROR, event, **fields)
