"""Bringing a database's schema to the newest Alembic revision (alembic/versions), run by the pod's migrate init
container before the app starts.

Everything happens in one transaction that first takes MIGRATE_LOCK, so two pods starting at once take turns and a
revision that fails leaves the database as it was (Postgres DDL is transactional). A database that does not sort text
by byte is refused before anything is applied. A database already past this build's revisions (a rollback to an older
image) is left as it is: the schema is expand-then-contract (docs/engineering.md), so the older build runs on it. A
revision waits at most LOCK_TIMEOUT_S for a table's lock, so a long reader fails the migrate (and the init container
retries) instead of every query queueing behind it."""

import logging
import time
from pathlib import Path

import psycopg
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.pool import NullPool

from .. import logs

log = logging.getLogger("ashfall.migrate")

SCRIPTS = Path(__file__).with_name("alembic")
MIGRATE_LOCK = 0x61736866   # 'ashf'
BYTE_ORDER = ("C", "POSIX")
LOCK_TIMEOUT_S = 5.0


class WrongCollation(RuntimeError):
    """The database sorts text by a locale's rules; seeded orders need byte order."""


def _config(conn: Connection, scripts: Path) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(scripts))
    cfg.attributes["connection"] = conn
    return cfg


def _check_collation(conn: Connection) -> None:
    row = conn.execute(text(
        "SELECT datcollate, datctype FROM pg_database WHERE datname = current_database()")).one()
    if row.datcollate not in BYTE_ORDER or row.datctype not in BYTE_ORDER:
        raise WrongCollation(f"collation {row.datcollate}, ctype {row.datctype}; create the database with LOCALE 'C'")


def ahead(revision: str, scripts: Path = SCRIPTS) -> bool:
    """A revision `scripts` does not hold: a newer build's, already applied."""
    return revision not in {r.revision for r in ScriptDirectory(str(scripts)).walk_revisions()}


def head(scripts: Path = SCRIPTS) -> str | None:
    return ScriptDirectory(str(scripts)).get_current_head()


def migrate(url: str, scripts: Path = SCRIPTS, lock_timeout_s: float = LOCK_TIMEOUT_S) -> str:
    """The database at `url` brought to the head of `scripts`, or left as it is when it is ahead of them; the revision
    it ends at."""
    t0 = time.monotonic()
    engine = create_engine("postgresql+psycopg://", creator=lambda: psycopg.connect(url), poolclass=NullPool)
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": MIGRATE_LOCK})
            _check_collation(conn)
            was = MigrationContext.configure(conn).get_current_revision()
            logs.info(log, "migrate.start", was=was or "none")
            if was is not None and ahead(was, scripts):
                logs.info(log, "migrate.ahead", revision=was, head=head(scripts) or "none")
                return was
            conn.execute(text(f"SET LOCAL lock_timeout = '{int(lock_timeout_s * 1000)}ms'"))
            command.upgrade(_config(conn, scripts), "head")
            now = MigrationContext.configure(conn).get_current_revision()
    except Exception:
        log.error("migrate.failed", extra={"fields": {}}, exc_info=True)   # the type chain and frames, never a message
        raise
    finally:
        engine.dispose()
    if now is None:
        raise RuntimeError(f"{scripts} has no revisions")
    logs.info(log, "migrate.done", was=was or "none", revision=now, ms=int((time.monotonic() - t0) * 1000))
    return now
