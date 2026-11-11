"""The app's database: a SQLAlchemy Core engine whose connections come from a psycopg pool.

SQLAlchemy keeps no pool of its own (NullPool): closing a connection hands it back to the psycopg pool
(`close_returns`), which checks it before lending it again (writable.py), so a connection a switchover killed or
turned read-only is replaced rather than handed to a request. Credentials come from libpq's environment (PGUSER, PGPASSWORD), never the URL."""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg_pool import ConnectionPool
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import NullPool

from .. import logs
from . import failover
from .migrate import SCRIPTS, ahead, head
from .writable import refuse_read_only_and_drain

log = logging.getLogger("ashfall.db")

CONNECT_TIMEOUT_S = 3
"""How long libpq waits on one host before trying the next, unless the URL sets `connect_timeout`: without it a host
that drops packets (a lost site) holds each new connection for the kernel's TCP timeout."""

TCP_SETTINGS = {"tcp_user_timeout": 6000, "keepalives": 1, "keepalives_idle": 2, "keepalives_interval": 1,
                "keepalives_count": 3}
"""libpq settings, each added unless the URL sets its own, that end a wait on a server whose packets vanish: a query in
flight errors after tcp_user_timeout (6 s) and an idle connection after about 5 s of silence, where the kernel would
retry for about fifteen minutes. They detect a lost peer, not a slow statement: a healthy long query is unaffected."""


class SchemaBehind(RuntimeError):
    """The database is at an older revision than this build's newest: this build's migrate has not run."""


@dataclass(frozen=True)
class Database:
    engine: Engine
    pool: ConnectionPool[psycopg.Connection]

    def close(self) -> None:
        self.engine.dispose()
        self.pool.close()


def open_database(url: str, max_size: int = 4, timeout_s: float = 5.0) -> Database:
    """A pool on `url`, opened and holding one live connection, or an error within `timeout_s`. `url` may name several
    hosts with `target_session_attrs=read-write`: libpq keeps the first that takes writes. `timeout_s` is also the
    budget of every checkout, so a request with no writable member fails within it (PoolTimeout) rather than hangs.
    A connect to one host gives up after CONNECT_TIMEOUT_S unless `url` sets `connect_timeout`; TCP_SETTINGS likewise.
    The first read-only connection a checkout meets drains the pool, so the demoted member's other idle connections
    go with it."""
    set_by_url = conninfo_to_dict(url)
    url = make_conninfo(url, **{k: v for k, v in {"connect_timeout": CONNECT_TIMEOUT_S, **TCP_SETTINGS}.items()
                                if k not in set_by_url})
    pool: ConnectionPool[psycopg.Connection] = ConnectionPool(
        url, min_size=1, max_size=max_size, timeout=timeout_s, open=False, close_returns=True,
        check=lambda conn: refuse_read_only_and_drain(conn, pool), name="ashfall")
    pool.open(wait=True, timeout=timeout_s)
    engine = create_engine("postgresql+psycopg://", creator=pool.getconn, poolclass=NullPool)
    failover.track(engine)
    return Database(engine=engine, pool=pool)


def from_env(env: Mapping[str, str], scripts: Path = SCRIPTS) -> Database | None:
    """The database DATABASE_URL names, connected, with its schema revision logged; None when it names none (the app
    then serves without one). SchemaBehind when the database is behind this build's newest revision; one ahead of it
    (an older build rolled back to) serves."""
    url = env.get("DATABASE_URL", "")
    if not url:
        logs.info(log, "db.none")
        return None
    database = open_database(url)
    with database.engine.connect() as conn:
        revision = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    newest = head(scripts)
    if revision != newest and not ahead(revision, scripts):
        database.close()
        logs.error(log, "db.behind", revision=revision, head=newest or "none")
        raise SchemaBehind(f"the database is at {revision}, this build needs {newest}: run its migrate first")
    site = {"site": env["SITE"]} if env.get("SITE") else {}
    logs.info(log, "db.connected", revision=revision, pool_max=database.pool.max_size, **site)
    return database
