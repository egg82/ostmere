"""What a failover looks like to a request, and when the request may be asked again.

A failover error is SQLSTATE 25006 (read-only transaction), SQLSTATE class 08 (connection exception) or 57P (operator
intervention), a psycopg OperationalError with no SQLSTATE (the client lost the connection), or the pool timing out
with no writable connection. Whether a request that met one may be replayed turns on whether anything it wrote could
have committed: one whose COMMIT was sent after a write cannot be told from one that took effect, so a replay could
apply it twice. `track` watches that on an engine; the request's route class (api/replay.py) reads it."""
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg_pool import PoolTimeout
from sqlalchemy import Engine, event
from sqlalchemy.exc import DBAPIError


@dataclass(frozen=True)
class Failure:
    kind: str
    """readonly, connection, client or no_connection."""
    sqlstate: str
    """Empty when the error carries none."""


@dataclass
class Attempt:
    """One run of a request's handler: what its transactions did so far."""
    wrote: bool = False
    """The open transaction has run a statement that is not a read."""
    committed_write: bool = False
    """A transaction that wrote reached COMMIT, which may or may not have taken effect."""


_current: ContextVar[Attempt | None] = ContextVar("ashfall_attempt", default=None)


def classify(ex: BaseException) -> Failure | None:
    """The Failure `ex` is, or None when it is any other error."""
    err = ex.orig if isinstance(ex, DBAPIError) else ex
    if isinstance(err, PoolTimeout):
        return Failure("no_connection", "")
    if not isinstance(err, psycopg.Error):
        return None
    state = err.sqlstate or ""
    if state == "25006":
        return Failure("readonly", state)
    if state.startswith(("08", "57P")):
        return Failure("connection", state)
    if not state and isinstance(err, psycopg.OperationalError):
        return Failure("client", "")
    return None


def let_through(ex: BaseException) -> None:
    """For an `except Exception` that fails closed: re-raises a failover error, so the request is replayed or answered
    503 instead of refused as if the database had said no; returns for any other error."""
    if classify(ex) is not None:
        raise ex


def start_attempt() -> Attempt:
    """A fresh Attempt for the handler about to run, visible to the threads it runs on."""
    found = Attempt()
    _current.set(found)
    return found


def replayable(attempt: Attempt, failure: Failure) -> bool:
    """Whether the request that met `failure` may run again: not after a write reached COMMIT, and not when the pool
    already spent its whole budget finding a writable connection."""
    return not attempt.committed_write and failure.kind != "no_connection"


def is_write(statement: str) -> bool:
    return not statement.lstrip().upper().startswith(("SELECT", "SHOW"))


def track(engine: Engine) -> None:
    """Records on the current Attempt, for every transaction `engine` runs, whether a write reached COMMIT."""

    @event.listens_for(engine, "begin")
    def begin(conn: Any) -> None:
        if (found := _current.get()) is not None:
            found.wrote = False

    @event.listens_for(engine, "before_cursor_execute")
    def execute(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        if (found := _current.get()) is not None and is_write(statement):
            found.wrote = True

    @event.listens_for(engine, "commit")
    def commit(conn: Any) -> None:
        if (found := _current.get()) is not None and found.wrote:
            found.committed_write = True
