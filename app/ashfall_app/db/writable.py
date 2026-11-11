"""The pool's `check` for a database with one writable member among several."""
from contextlib import suppress
from typing import Any

import psycopg
from psycopg_pool import ConnectionPool


class ReadOnlyConnection(psycopg.OperationalError):
    """The connection is to a member that no longer takes writes."""


def refuse_read_only(conn: psycopg.Connection[Any]) -> None:
    """A pool `check` (psycopg_pool.ConnectionPool(check=...)): runs on every checkout, returns quietly when the
    connection answers and its next transaction would be read-write, and raises when it is not usable:
    ReadOnlyConnection when the server reports `transaction_read_only` on (a primary demoted by a failover, or a
    standby promoted past), psycopg's own error when the connection is closed or broken. A read-only connection is
    shut before the raise: the pool puts back a failed connection that is still open, so only a shut one is discarded.
    The pool then lends another, so a request never starts on a member that cannot take its writes. Leaves a usable
    connection idle, its autocommit as found."""
    restore = not conn.autocommit
    conn.autocommit = True
    try:
        row = conn.execute("SHOW transaction_read_only").fetchone()
    finally:
        if restore:
            with suppress(Exception):   # a closed connection: the execute above already raised
                conn.autocommit = False
    if row is None or row[0] != "off":
        conn.pgconn.finish()   # not close(): with close_returns a pooled connection's close() gives it back to the pool
        raise ReadOnlyConnection("the connection is read-only")


def refuse_read_only_and_drain(conn: psycopg.Connection[Any], pool: ConnectionPool[Any]) -> None:
    """`refuse_read_only` for a pool's `check`, which on a refusal also drains `pool`: the other idle connections went to
    the same demoted member, and left to be refused one by one the pool's backoff between failed checkouts spends the
    checkout budget. The drained connections are replaced by new ones, which reach the writable member."""
    try:
        refuse_read_only(conn)
    except ReadOnlyConnection:
        pool.drain()
        raise
