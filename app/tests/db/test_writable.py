"""The pool check that refuses a connection to a member that no longer takes writes (db/writable.py), on a real server."""
import time

import psycopg
import pytest
from psycopg.pq import TransactionStatus

from ashfall_app.db.writable import ReadOnlyConnection, refuse_read_only


def test_a_writable_connection_passes_and_is_left_idle(pg_url: str):
    with psycopg.connect(pg_url) as conn:
        refuse_read_only(conn)
        assert not conn.autocommit
        assert conn.info.transaction_status == TransactionStatus.IDLE
        assert not conn.closed


def test_a_read_only_connection_is_refused_and_shut(pg_url: str):
    conn = psycopg.connect(pg_url, autocommit=True)
    conn.execute("SET default_transaction_read_only = on")
    conn.autocommit = False
    with pytest.raises(ReadOnlyConnection):
        refuse_read_only(conn)
    assert conn.closed


def test_a_connection_the_server_dropped_is_refused(pg_url: str):
    conn = psycopg.connect(pg_url)
    with psycopg.connect(pg_url, autocommit=True) as admin:
        admin.execute("SELECT pg_terminate_backend(%s)", (conn.info.backend_pid,))
    with pytest.raises(psycopg.OperationalError):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:   # the server drops it a moment after the signal
            refuse_read_only(conn)
