"""One pool checkout per request, and one transaction where its writes allow (docs/decisions.md, "A database failover is
replayed once, or answered 503"). The route class opens a unit around each request (api/route.py); every `begin` or
`read` inside it runs on the unit's connection, taken from the pool at the first and held to the end. Outside a unit (startup, tools,
tests) each is a plain `engine.begin()`, its own checkout and transaction.

A `begin` block commits when it ends and rolls back when it raises, as `engine.begin()` does, so every write commits
where it did with a transaction of its own: a replay's test of whether a write reached COMMIT (failover.py) reads the
same. Its transaction also holds the `read` blocks before it. A `read` block runs only plain reads (no lock, no write)
and leaves its transaction open for the next block; `settle` ends one still open when the handler is done, and
`release` before a long computation that should hold no connection. Blocks do not nest."""
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from sqlalchemy import Connection, Engine


@dataclass
class _Unit:
    conn: Connection | None = None


_current: ContextVar[_Unit | None] = ContextVar("ashfall_unit", default=None)


@contextmanager
def scope() -> Generator[None]:
    """A unit for the request running in this context; its connection goes back to the pool when it ends."""
    found = _Unit()
    token = _current.set(found)
    try:
        yield
    finally:
        _current.reset(token)
        _close(found)


def begin(engine: Engine) -> AbstractContextManager[Connection]:
    """A connection in a transaction that commits when the block ends: the unit's, or `engine.begin()` outside one."""
    found = _current.get()
    return engine.begin() if found is None else _joined(found, engine, commit=True)


def read(engine: Engine) -> AbstractContextManager[Connection]:
    """`begin` for a block of plain reads: in a unit, its transaction stays open for the request's next block."""
    found = _current.get()
    return engine.begin() if found is None else _joined(found, engine, commit=False)


def settle() -> None:
    """Commits the unit's open transaction, which holds only reads; does nothing outside a unit or with none open."""
    found = _current.get()
    if found is not None and found.conn is not None and found.conn.in_transaction():
        found.conn.commit()


def release() -> None:
    """`settle`, then gives the unit's connection back to the pool, for a request about to compute for long holding
    none; its next block takes another."""
    settle()
    discard()


def discard() -> None:
    """Gives the unit's connection back after a failover, so the request's replay takes a new one from the pool."""
    found = _current.get()
    if found is not None:
        _close(found)


@contextmanager
def _joined(found: _Unit, engine: Engine, commit: bool) -> Generator[Connection]:
    if found.conn is None:
        found.conn = engine.connect()
    conn = found.conn
    try:
        yield conn
    except BaseException:
        if conn.in_transaction():
            conn.rollback()
        raise
    if commit:
        conn.commit()


def _close(found: _Unit) -> None:
    conn, found.conn = found.conn, None
    if conn is not None:
        conn.close()
