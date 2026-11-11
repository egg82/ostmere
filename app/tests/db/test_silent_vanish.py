"""A member whose site vanished without closing the connection (packets dropped, no RST), under a query already running
on it: the pool's TCP settings (db/engine.py TCP_SETTINGS) turn the wait into a failover error within seconds.

`podman pause` does not do this (the host kernel still acknowledges), so tools/silent_vanish.sh runs Postgres in a
network namespace of its own, runs these tests inside it, and, when a test creates $ASHFALL_VANISH/drop, drops every
packet there with iptables. CI has no such privilege, so without the harness these tests skip. Each waits longer than
the suite's 6 s timeout, so each sets its own."""

import os
import threading
import time
from pathlib import Path

import psycopg
import pytest
from sqlalchemy import text

from ashfall_app.db import failover
from ashfall_app.db.engine import Database, open_database

HARNESS = os.environ.get("ASHFALL_VANISH", "")
pytestmark = pytest.mark.skipif(
    not HARNESS, reason="needs the silent-vanish harness (app/tools/silent_vanish.sh): iptables inside the server's network namespace")

URL = "postgresql://postgres@127.0.0.1:55460/postgres"
BOUND_S = 7.0
"""tcp_user_timeout (6 s) plus the time to notice; the replay budget is longer."""
CONTROL_S = 20.0


def vanish() -> None:
    signal = Path(HARNESS)
    (signal / "drop").touch()
    for _ in range(100):
        if (signal / "dropped").exists():
            return
        time.sleep(0.1)
    raise AssertionError("the harness never dropped the packets")


def run_in_thread(fn: object) -> tuple[threading.Thread, list[tuple[str, BaseException | None, float]]]:
    """(thread, outcome): outcome gets ("done", None, seconds) or ("error", exception, seconds) when fn returns or raises."""
    outcome: list[tuple[str, BaseException | None, float]] = []
    t0 = time.monotonic()

    def go() -> None:
        try:
            assert callable(fn)
            fn()
            outcome.append(("done", None, time.monotonic() - t0))
        except Exception as e:
            outcome.append(("error", e, time.monotonic() - t0))
    t = threading.Thread(target=go, daemon=True)
    t.start()
    return t, outcome


def started(statement: str) -> None:
    """`statement` is running on the server."""
    with psycopg.connect(URL, autocommit=True, connect_timeout=3) as m:
        for _ in range(100):
            if m.execute("SELECT count(*) FROM pg_stat_activity WHERE query LIKE %s AND state = 'active'"
                         " AND pid <> pg_backend_pid()", (f"%{statement}%",)).fetchone() != (0,):
                return
            time.sleep(0.05)
    raise AssertionError("the statement never started")


def query(database: Database, statement: str) -> None:
    with database.engine.connect() as conn:
        conn.execute(text(statement))


@pytest.mark.timeout(25)
def test_a_query_in_flight_on_a_member_that_vanished_fails_over_within_the_bound():
    database = open_database(URL)
    try:
        t, outcome = run_in_thread(lambda: query(database, "SELECT pg_sleep(31)"))
        started("pg_sleep(31)")
        vanish()
        t.join(BOUND_S + 3)
        assert outcome and outcome[0][0] == "error", outcome
        _, exc, took = outcome[0]
        assert exc is not None and failover.classify(exc) is not None, repr(exc)
        print(f"failed over after {took:.1f} s")
        assert took < BOUND_S, took
    finally:
        database.close()


@pytest.mark.timeout(40)
def test_without_the_settings_the_same_vanish_is_still_waiting_long_after_the_bound():
    """The control: the drop is silent, so only the settings end the wait."""
    c = psycopg.connect(URL, autocommit=True, connect_timeout=3)
    t, outcome = run_in_thread(lambda: c.execute("SELECT pg_sleep(61)"))
    started("pg_sleep(61)")
    vanish()
    t.join(CONTROL_S)
    assert CONTROL_S > BOUND_S * 2 and not outcome, outcome


@pytest.mark.timeout(30)
def test_a_slow_but_healthy_statement_completes():
    """The settings detect a vanished server, not a long query: this statement outlives tcp_user_timeout."""
    database = open_database(URL)
    try:
        t0 = time.monotonic()
        with database.engine.connect() as conn:
            assert conn.execute(text("SELECT pg_sleep(12), 7")).one()[1] == 7
        assert time.monotonic() - t0 >= 12
    finally:
        database.close()
