"""Revision 0013 (the journal's days): a save the build before wrote, days into its game, migrates with no days stored
and composes every day it has begun on its next step, its subject's line written on the day it fell on."""
import shutil
from pathlib import Path

import psycopg
import pytest

from ashfall_app.db.migrate import SCRIPTS, head, migrate
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.journal import DAY_S
from tests.db.stored.test_save_lessons_migrate import ACCOUNT_COLUMNS, SAVE_COLUMNS, SESSION_COLUMNS, copy_rows
from tests.game_client import game_client
from tests.saves.journal_fixture import a_beat_line


def test_a_save_from_before_the_journal_was_stored_composes_its_days_on_its_next_step(
        pg_url: str, pg_empty: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, shipped_opening: Opening):
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    for later in (scripts / "versions").glob("*.py"):
        if later.name[:4].isdigit() and int(later.name[:4]) >= 13:
            later.unlink()
    assert migrate(pg_empty, scripts) == "0012"
    with game_client(pg_url, monkeypatch) as made:
        save_id = made.begin()["save"]["save_id"]
        cookies = dict(made.client.cookies)
    assert [copy_rows(pg_url, pg_empty, t, c) for t, c in
            (("accounts", ACCOUNT_COLUMNS), ("sessions", SESSION_COLUMNS), ("saves", SAVE_COLUMNS))] == [1, 1, 1]
    key, subject = a_beat_line(shipped_opening)
    with psycopg.connect(pg_empty) as c:
        c.execute("INSERT INTO save_lines (save_id, n, at, key) VALUES (%s, 0, %s, %s)", (save_id, DAY_S + 30, key))
    assert migrate(pg_empty) == head()
    with game_client(pg_empty, monkeypatch) as later:
        later.client.cookies.update(cookies)
        later.clock.tick(3 * DAY_S + 60)
        opened = later.client.post(f"/api/saves/{save_id}/open")
        assert opened.status_code == 200, opened.text
    with psycopg.connect(pg_empty) as c:
        days = c.execute("SELECT day, notes FROM save_journal WHERE save_id = %s ORDER BY day", (save_id,)).fetchall()
    assert [d for d, _ in days] == [0, 1, 2, 3]
    assert [[n["subject"] for n in notes] for _, notes in days][1] == [subject]
    served = opened.json()
    assert served["journal_days"] == [] and [d["day"] for d in served["step"]["journal_days"]] == [1]
