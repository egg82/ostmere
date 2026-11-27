"""Revision 0019: a journal day the build before 0015 stored whole (`through` null) is closed at its day's end, its notes
as stored; a day with a `through` keeps it; and the column takes no null after."""
import shutil
from pathlib import Path

import psycopg
import pytest
from psycopg.types.json import Jsonb

from ashfall_app.db.migrate import SCRIPTS, head, migrate
from ashfall_app.saves.journal import DAY_S
from tests.db.stored.test_save_lessons_migrate import ACCOUNT_COLUMNS, SAVE_COLUMNS, SESSION_COLUMNS, copy_rows
from tests.game_client import game_client

NOTES = [{"subject": "s_b", "slot": "first", "key": "k.b"}, {"subject": "s_a", "slot": "first", "key": "k.a"}]


def test_a_day_stored_whole_is_closed_at_its_end_and_through_takes_no_null(
        pg_url: str, pg_empty: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    for later in (scripts / "versions").glob("*.py"):
        if later.name[:4].isdigit() and int(later.name[:4]) >= 19:
            later.unlink()
    assert migrate(pg_empty, scripts) == "0018"
    with game_client(pg_url, monkeypatch) as made:
        save_id = made.begin()["save"]["save_id"]
    assert [copy_rows(pg_url, pg_empty, t, c) for t, c in
            (("accounts", ACCOUNT_COLUMNS), ("sessions", SESSION_COLUMNS), ("saves", SAVE_COLUMNS))] == [1, 1, 1]
    with psycopg.connect(pg_empty) as c:
        c.execute("INSERT INTO save_journal (save_id, day, notes, through) VALUES (%s, 2, %s, NULL), (%s, 3, %s, %s)",
                  (save_id, Jsonb(NOTES), save_id, Jsonb([]), 3 * DAY_S + 7))
    assert migrate(pg_empty) == head()
    with psycopg.connect(pg_empty) as c:
        days = c.execute("SELECT day, notes, through FROM save_journal WHERE save_id = %s ORDER BY day",
                         (save_id,)).fetchall()
        assert days == [(2, NOTES, 3 * DAY_S), (3, [], 3 * DAY_S + 7)]
        with pytest.raises(psycopg.errors.NotNullViolation):
            c.execute("INSERT INTO save_journal (save_id, day, notes) VALUES (%s, 4, '[]'::jsonb)", (save_id,))
