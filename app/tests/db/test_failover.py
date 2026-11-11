"""A failover under a request, against the real Postgres the tests run on: the app discards the connection and replays
the whole request once, answers 503 save_unavailable when it must not replay or the replay fails too, and a pooled
connection to a member that went read-only is never lent.

Each fault is injected into the app's own connection by an engine event, at the statement or the COMMIT the test names,
and is the server's: SET TRANSACTION READ ONLY (the server then refuses the write with SQLSTATE 25006) or
pg_terminate_backend (the connection drops)."""
import socket
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from sqlalchemy import Engine, event, text

from ashfall_app.db.engine import Database, from_env, open_database
from tests.game_client import GameClient

Fault = Callable[[Any], None]


def pid_gone(url: str, pid: int) -> bool:
    with psycopg.connect(url, autocommit=True) as c:
        return c.execute("SELECT count(*) FROM pg_stat_activity WHERE pid = %s", (pid,)).fetchone() == (0,)


def terminate(url: str) -> Fault:
    """Drops the connection the statement is about to run on, and returns once the server has."""
    def fault(dbapi: Any) -> None:
        pid = dbapi.info.backend_pid
        with psycopg.connect(url, autocommit=True) as c:
            c.execute("SELECT pg_terminate_backend(%s)", (pid,))
        deadline = time.monotonic() + 3
        while not pid_gone(url, pid) and time.monotonic() < deadline:
            pass
    return fault


def read_only_transaction(dbapi: Any) -> None:
    dbapi.execute("SET TRANSACTION READ ONLY")


def is_write(statement: str) -> bool:
    return not statement.lstrip().upper().startswith(("SELECT", "SHOW"))


def at_statement(engine: Engine, fault: Fault, matching: Callable[[str], bool] = is_write) -> None:
    """Runs `fault` on the connection once, just before the first statement `matching` accepts (by default a write)."""
    fired: list[bool] = []

    @event.listens_for(engine, "before_cursor_execute")
    def before(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        if not fired and matching(statement):
            fired.append(True)
            fault(cursor.connection)


def at_commit(engine: Engine, fault: Fault) -> None:
    """Runs `fault` on the connection once, just before the first COMMIT that follows a write."""
    wrote: list[bool] = []
    fired: list[bool] = []

    @event.listens_for(engine, "before_cursor_execute")
    def write(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        if is_write(statement):
            wrote.append(True)

    @event.listens_for(engine, "commit")
    def commit(conn: Any) -> None:
        if wrote and not fired:
            fired.append(True)
            fault(conn.connection.dbapi_connection)


def writes(engine: Engine) -> list[str]:
    """The write statements the engine runs, as they come."""
    seen: list[str] = []

    @event.listens_for(engine, "before_cursor_execute")
    def before(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        if is_write(statement):
            seen.append(statement)
    return seen


def into_accounts(statement: str) -> bool:
    return statement.lstrip().upper().startswith("INSERT INTO ACCOUNTS")


def accounts(url: str) -> int:
    with psycopg.connect(url) as c:
        row = c.execute("SELECT count(*) FROM accounts").fetchone()
    assert row is not None
    return int(row[0])


def engine_of(game: GameClient) -> Engine:
    database: Database = game.app.state.db
    return database.engine


def multi_host(url: str, first: str = "127.0.0.1", first_port: int = 1) -> str:
    """The conninfo a two-site deploy uses: a first host nothing answers, then the real one, read-write wanted. Every
    other setting of `url` (user, password, database) is kept; a url without a port names the default one."""
    d = conninfo_to_dict(url)
    return make_conninfo(url, host=f"{first},{d.get('host', 'localhost')}", port=f"{first_port},{d.get('port', 5432)}",
                         target_session_attrs="read-write")


def test_a_read_only_refusal_replays_the_request_once_and_it_succeeds(
        game: GameClient, pg_url: str, capsys: pytest.CaptureFixture[str]):
    at_statement(engine_of(game), read_only_transaction)
    r = game.client.post("/api/saves")
    assert r.status_code == 200, r.text
    assert accounts(pg_url) == 1
    assert "event=db.failover kind=readonly sqlstate=25006 replayed=true" in capsys.readouterr().out


def test_a_terminated_connection_replays_the_request(game: GameClient, pg_url: str):
    at_statement(engine_of(game), terminate(pg_url))
    r = game.client.post("/api/saves")
    assert r.status_code == 200, r.text
    assert accounts(pg_url) == 1


def test_a_connection_lost_at_commit_is_not_replayed(game: GameClient, pg_url: str,
                                                     capsys: pytest.CaptureFixture[str]):
    """Whether the COMMIT happened is unknown: a replay could apply the request twice."""
    save_id = game.begin()["save"]["save_id"]
    engine = engine_of(game)
    seen = writes(engine)
    at_commit(engine, terminate(pg_url))
    r = game.advance(save_id)
    assert seen, "the advance wrote nothing: the fault never fired"
    assert r.status_code == 503, r.text
    assert r.json()["code"] == "save_unavailable"
    assert r.headers["Retry-After"] == "3"
    assert len(seen) == len(set(seen))
    assert "replayed=false" in capsys.readouterr().out


def test_a_failure_after_an_earlier_transaction_committed_is_not_replayed(game: GameClient, pg_url: str):
    """The limit count commits before the account is made: a replay would count the try twice."""
    engine = engine_of(game)
    seen = writes(engine)
    at_statement(engine, read_only_transaction, into_accounts)
    r = game.client.post("/api/saves")
    assert r.status_code == 503, r.text
    assert sum(into_accounts(s) for s in seen) == 1
    assert accounts(pg_url) == 0


def test_a_pooled_connection_gone_read_only_is_not_lent(game: GameClient, pg_url: str):
    database: Database = game.app.state.db
    with database.pool.connection() as c:
        c.autocommit = True
        c.execute("SET default_transaction_read_only = on")
        c.autocommit = False
    r = game.client.post("/api/saves")
    assert r.status_code == 200, r.text


def test_every_idle_connection_to_a_demoted_server_is_replaced_within_the_checkout_budget(game: GameClient):
    database: Database = game.app.state.db
    held = [database.pool.getconn() for _ in range(database.pool.max_size)]
    for c in held:
        c.autocommit = True
        c.execute("SET default_transaction_read_only = on")
        c.autocommit = False
        database.pool.putconn(c)
    started = time.monotonic()
    r = game.client.post("/api/saves")
    assert r.status_code == 200, r.text
    assert time.monotonic() - started < database.pool.timeout


@contextmanager
def silent_host() -> Generator[int]:
    """A port that takes the TCP connection and never answers the startup packet, as a site whose packets vanish does:
    the connect hangs until libpq's connect_timeout, with no privilege needed."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen(8)
        yield int(s.getsockname()[1])


def test_a_host_that_never_answers_is_passed_over_within_a_few_seconds(pg_url: str):
    """Opened on a thread that is left behind if it hangs: a pool stuck connecting cannot be closed until libpq gives up."""
    opened: list[Database] = []
    with silent_host() as port:
        opener = threading.Thread(
            target=lambda: opened.append(open_database(multi_host(pg_url, first_port=port), timeout_s=30)), daemon=True)
        opener.start()
        opener.join(4)
        assert opened, "no connection to the second host within 4 s"
    with opened[0].engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar_one() == 1
    opened[0].close()


def test_a_connect_timeout_the_url_sets_is_kept(pg_url: str):
    database = open_database(make_conninfo(pg_url, connect_timeout=9))
    try:
        with database.pool.connection() as conn:
            assert conn.info.get_parameters()["connect_timeout"] == "9"
    finally:
        database.close()


TCP = {"tcp_user_timeout": "6000", "keepalives": "1", "keepalives_idle": "2", "keepalives_interval": "1", "keepalives_count": "3"}


def test_the_tcp_settings_are_added_to_a_url_that_sets_none(pg_url: str):
    database = open_database(pg_url)
    try:
        with database.pool.connection() as conn:
            params = conn.info.get_parameters()
        assert {k: params.get(k) for k in TCP} == TCP
    finally:
        database.close()


def test_a_tcp_setting_the_url_sets_is_kept_and_the_others_are_added(pg_url: str):
    database = open_database(make_conninfo(pg_url, tcp_user_timeout=1234, keepalives_idle=9))
    try:
        with database.pool.connection() as conn:
            params = conn.info.get_parameters()
        assert {k: params.get(k) for k in TCP} == {**TCP, "tcp_user_timeout": "1234", "keepalives_idle": "9"}
    finally:
        database.close()


def test_getconn_fails_within_its_budget_when_no_host_is_writable(pg_url: str):
    url = make_conninfo(pg_url, target_session_attrs="read-write")
    database = open_database(url, timeout_s=0.5)
    name = str(conninfo_to_dict(pg_url)["dbname"])
    try:
        with psycopg.connect(pg_url, autocommit=True) as c:
            c.execute(sql.SQL("ALTER DATABASE {} SET default_transaction_read_only = on").format(sql.Identifier(name)))
            c.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                      "WHERE datname = %s AND pid <> pg_backend_pid()", (name,))
        started = time.monotonic()
        with pytest.raises(Exception):
            with database.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        assert time.monotonic() - started < 2
    finally:
        database.close()


def test_a_multi_host_url_is_accepted_unchanged(pg_url: str):
    database = open_database(multi_host(pg_url))
    try:
        with database.engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        database.close()


def test_the_site_is_logged_at_startup(pg_url: str, capsys: pytest.CaptureFixture[str]):
    database = from_env({"DATABASE_URL": multi_host(pg_url), "SITE": "site-a"})
    assert database is not None
    database.close()
    out = capsys.readouterr().out
    assert "event=db.connected" in out
    assert "site=site-a" in out
