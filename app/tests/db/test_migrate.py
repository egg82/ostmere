"""migrate.py: up from empty, idempotent, one transaction under one lock, and refusing what it must refuse."""
import shutil
import threading
import time
import uuid
from pathlib import Path

import psycopg
import pytest
from psycopg import sql
from sqlalchemy.exc import OperationalError, ProgrammingError

from ashfall_app import logs
from ashfall_app.db import __main__ as cli
from ashfall_app.db.migrate import MIGRATE_LOCK, SCRIPTS, WrongCollation, head, migrate
from tests import pg

HEAD = head()
TABLES = {"accounts", "sessions", "saves", "save_lines", "save_decisions", "save_snapshots", "save_manifests", "tries",
          "feedback", "transfer_codes", "reminder_devices"}


def tables(url: str) -> set[str]:
    with psycopg.connect(url) as c:
        rows = c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'").fetchall()
    return {r[0] for r in rows}


def revision(url: str) -> str | None:
    with psycopg.connect(url) as c:
        if not c.execute("SELECT to_regclass('alembic_version') IS NOT NULL").fetchone() == (True,):
            return None
        row = c.execute("SELECT version_num FROM alembic_version").fetchone()
    return row[0] if row else None


def test_an_empty_database_migrates_to_head_and_again_is_a_no_op(pg_empty: str, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    assert tables(pg_empty) == set()
    assert migrate(pg_empty) == HEAD
    assert tables(pg_empty) == TABLES | {"alembic_version"}
    assert migrate(pg_empty) == HEAD
    out = capsys.readouterr().out
    assert f"event=migrate.done was=none revision={HEAD}" in out and f"event=migrate.done was={HEAD} revision={HEAD}" in out


def test_a_failing_revision_leaves_the_database_as_it_was(pg_empty: str, tmp_path: Path,
                                                          capsys: pytest.CaptureFixture[str]):
    logs.setup()
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    (scripts / "versions" / "0098_planted.py").write_text(
        f'from alembic import op\nrevision = "0098"\ndown_revision = "{HEAD}"\n'
        'def upgrade() -> None:\n    op.execute("ALTER TABLE no_such_table ADD COLUMN x int")\n')
    with pytest.raises(ProgrammingError, match="no_such_table"):
        migrate(pg_empty, scripts)
    assert tables(pg_empty) == set() and revision(pg_empty) is None   # every revision rolled back with it
    assert "event=migrate.failed" in capsys.readouterr().out


def test_a_database_that_sorts_by_locale_is_refused(pg_admin: str):
    name = "t_" + uuid.uuid4().hex[:16]
    with psycopg.connect(pg_admin, autocommit=True) as c:
        c.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0 ENCODING 'UTF8' LOCALE 'en_US.utf8'").format(
            sql.Identifier(name)))
    url = pg.with_db(pg_admin, name)
    try:
        with pytest.raises(WrongCollation):
            migrate(url)
        assert tables(url) == set()
    finally:
        pg.drop(url)


def test_a_second_migrate_waits_for_the_lock(pg_empty: str):
    done = threading.Event()
    with psycopg.connect(pg_empty, autocommit=True) as holder:
        holder.execute("SELECT pg_advisory_lock(%s)", (MIGRATE_LOCK,))
        worker = threading.Thread(target=lambda: (migrate(pg_empty), done.set()))
        worker.start()
        assert not done.wait(0.2), "migrate ran while another process held the lock"
        holder.execute("SELECT pg_advisory_unlock(%s)", (MIGRATE_LOCK,))
        worker.join(5)
    assert done.is_set() and revision(pg_empty) == HEAD


def test_the_command(pg_empty: str, monkeypatch: pytest.MonkeyPatch):
    assert cli.main([]) == 2
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli.main(["migrate"]) == 2
    monkeypatch.setenv("DATABASE_URL", pg_empty)
    assert cli.main(["migrate"]) == 0 and revision(pg_empty) == HEAD


def test_a_database_ahead_of_these_revisions_is_left_as_it_is(pg_url: str, capsys: pytest.CaptureFixture[str]):
    """A rollback to an older image: its migrate meets a newer build's revision, does nothing and succeeds (the schema
    is expand-then-contract, so the older build runs on it)."""
    logs.setup()
    with psycopg.connect(pg_url) as c:
        c.execute("UPDATE alembic_version SET version_num = '0099'")
    assert migrate(pg_url) == "0099" and revision(pg_url) == "0099"
    out = capsys.readouterr().out
    assert f"event=migrate.ahead revision=0099 head={HEAD}" in out and "event=migrate.done" not in out


def test_the_command_exits_zero_when_ahead(pg_url: str, monkeypatch: pytest.MonkeyPatch):
    with psycopg.connect(pg_url) as c:
        c.execute("UPDATE alembic_version SET version_num = '0099'")
    monkeypatch.setenv("DATABASE_URL", pg_url)
    assert cli.main(["migrate"]) == 0 and revision(pg_url) == "0099"


def planted(tmp_path: Path, upgrade: str) -> Path:
    """These revisions plus a 0098 running `upgrade`."""
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    (scripts / "versions" / "0098_planted.py").write_text(
        f'from alembic import op\nrevision = "0098"\ndown_revision = "{HEAD}"\n'
        f'def upgrade() -> None:\n    op.execute("{upgrade}")\n')
    return scripts


def test_a_revision_waits_for_a_table_lock_only_so_long(pg_url: str, tmp_path: Path):
    """A long reader holds a table a revision alters: the migrate gives up at the lock timeout and changes nothing,
    rather than queueing every query behind it. Control: with the reader gone the same revision applies."""
    scripts = planted(tmp_path, "ALTER TABLE accounts ADD COLUMN planted int")
    with psycopg.connect(pg_url) as reader:
        reader.execute("LOCK TABLE accounts IN ACCESS SHARE MODE")
        t0 = time.monotonic()
        with pytest.raises(OperationalError, match="lock timeout"):
            migrate(pg_url, scripts, lock_timeout_s=0.2)
        assert time.monotonic() - t0 < 2
    assert revision(pg_url) == HEAD
    assert migrate(pg_url, scripts, lock_timeout_s=0.2) == "0098"
