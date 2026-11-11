"""The app serves as before with no database configured, and with DATABASE_URL connects at start and says so."""
import shutil
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from ashfall_app import logs
from ashfall_app.db.engine import SchemaBehind, from_env
from ashfall_app.db.migrate import SCRIPTS, head
from ashfall_app.main import create_app


def test_without_a_database_the_app_starts_and_serves(monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture[str]):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = create_app()
    assert app.state.db is None
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
    assert "event=db.none" in capsys.readouterr().out


def test_with_a_database_the_app_connects_at_start(pg_url: str, monkeypatch: pytest.MonkeyPatch,
                                                   capsys: pytest.CaptureFixture[str]):
    monkeypatch.setenv("DATABASE_URL", pg_url)
    app = create_app()
    assert f"event=db.connected revision={head()}" in capsys.readouterr().out
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        with app.state.db.engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM accounts")).scalar_one() == 0
    assert app.state.db.pool.closed   # the app's shutdown closed it



def test_a_database_behind_this_build_is_refused(pg_url: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                 capsys: pytest.CaptureFixture[str]):
    """This build's migrate has not run (the database is at head, the planted newest is 0098): the app does not start
    on it."""
    logs.setup()
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    (scripts / "versions" / "0098_planted.py").write_text(
        f'revision = "0098"\ndown_revision = "{head()}"\ndef upgrade() -> None:\n    pass\n')
    with pytest.raises(SchemaBehind, match=head() or "none"):
        from_env({"DATABASE_URL": pg_url}, scripts)
    assert f"event=db.behind revision={head()} head=0098" in capsys.readouterr().out


def test_a_database_ahead_of_this_build_serves(pg_url: str, capsys: pytest.CaptureFixture[str]):
    """A rollback: the database holds a newer build's revision, and the older build serves on it."""
    logs.setup()
    with psycopg.connect(pg_url) as c:
        c.execute("UPDATE alembic_version SET version_num = '0099'")
    database = from_env({"DATABASE_URL": pg_url})
    assert database is not None
    database.close()
    assert "event=db.connected revision=0099" in capsys.readouterr().out
