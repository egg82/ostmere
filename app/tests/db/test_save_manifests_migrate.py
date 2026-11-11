"""Revision 0012 (manifests stored once): a save the build before wrote opens under it, the app's start stores its
manifest under its digest, and the save is written back without it, read whole again with the one held."""
import shutil
from pathlib import Path

import psycopg
import pytest

from ashfall_app.db.manifests import stripped, whole
from ashfall_app.db.migrate import SCRIPTS, head, migrate
from tests.db.test_save_lessons_migrate import ACCOUNT_COLUMNS, SAVE_COLUMNS, SESSION_COLUMNS, copy_rows
from tests.game_client import game_client


def test_a_save_from_before_manifests_were_stored_opens_and_is_written_stripped(
        pg_url: str, pg_empty: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    for later in (scripts / "versions").glob("*.py"):
        if later.name[:4].isdigit() and int(later.name[:4]) >= 12:
            later.unlink()
    assert migrate(pg_empty, scripts) == "0011"
    with game_client(pg_url, monkeypatch) as made:
        save_id = made.begin()["save"]["save_id"]
        cookies = dict(made.client.cookies)
    assert [copy_rows(pg_url, pg_empty, t, c) for t, c in
            (("accounts", ACCOUNT_COLUMNS), ("sessions", SESSION_COLUMNS), ("saves", SAVE_COLUMNS))] == [1, 1, 1]
    assert migrate(pg_empty) == head()
    with game_client(pg_empty, monkeypatch) as old:
        old.client.cookies.update(cookies)
        opened = old.client.post(f"/api/saves/{save_id}/open")
        assert opened.status_code == 200, opened.text
    with psycopg.connect(pg_empty) as c:
        digest, state = c.execute("SELECT rules_digest, state FROM saves WHERE id = %s", [save_id]).fetchone() or ("", "")
        held = c.execute("SELECT rules_digest, manifest FROM save_manifests").fetchall()
    assert [d for d, _ in held] == [digest]
    manifest = held[0][1]
    assert '"manifest":' not in state and stripped(whole(state, manifest)) == (state, manifest)
