"""Revision 0010 (lessons per save): a save and an account written by the build before it load under it. The save opens
with nothing kept about its teaching, whatever lessons its account kept then, as does a new game of that account, and
the account's lessons are on."""
import shutil
from pathlib import Path

import psycopg
import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

from ashfall_app.db.migrate import SCRIPTS, head, migrate
from tests.game_client import game_client

OLD_ACCOUNT = {"rule_seen": True, "rules_opened": True, "lessons": ["first_mix", "first_rule"],
               "lesson_ends": [{"lesson": "first_mix", "skipped": False, "step": 6, "longest_wait_s": 4}]}
"""What the build before kept on an account that had played the first lessons."""
ACCOUNT_COLUMNS = ("id", "created_at", "last_seen_at", "words_hash", "words_made_at")
SESSION_COLUMNS = ("id", "account_id", "token_hash", "created_at", "last_seen_at", "label")
SAVE_COLUMNS = ("id", "account_id", "created_at", "started_at", "updated_at", "state", "format", "rules_digest",
                "decisions", "game_time", "ended_at", "deleted_at", "build", "release", "number", "camp_level",
                "rule_runs")


def copy_rows(source: str, target: str, table: str, columns: tuple[str, ...]) -> int:
    """Copies `table`'s rows, these columns only (the build before had no others), keeping their ids."""
    names = sql.SQL(", ").join(sql.Identifier(c) for c in columns)
    with psycopg.connect(source) as src:
        rows: list[tuple[object, ...]] = src.execute(
            sql.SQL("SELECT {} FROM {}").format(names, sql.Identifier(table))).fetchall()
    insert = sql.SQL("INSERT INTO {} ({}) OVERRIDING SYSTEM VALUE VALUES ({})").format(
        sql.Identifier(table), names, sql.SQL(", ").join(sql.Placeholder() * len(columns)))
    with psycopg.connect(target) as dst:
        for row in rows:
            dst.execute(insert, [Jsonb(v) if isinstance(v, (dict, list)) else v for v in row])
        dst.execute(sql.SQL("SELECT setval(pg_get_serial_sequence({t}, 'id'), (SELECT max(id) FROM {i}))").format(
            t=sql.Literal(table), i=sql.Identifier(table)))   # an id given by hand moves no identity on
    return len(rows)


def test_a_save_from_before_lessons_were_per_save_opens_with_none_kept(pg_url: str, pg_empty: str, tmp_path: Path,
                                                                      monkeypatch: pytest.MonkeyPatch):
    scripts = tmp_path / "alembic"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    for later in (scripts / "versions").glob("*.py"):
        if later.name[:4].isdigit() and int(later.name[:4]) >= 10:
            later.unlink()
    assert migrate(pg_empty, scripts) == "0009"
    with game_client(pg_url, monkeypatch) as made:   # a real save and session to stand for the build before's
        save_id = made.begin()["save"]["save_id"]
        cookies = dict(made.client.cookies)
    assert [copy_rows(pg_url, pg_empty, t, c) for t, c in
            (("accounts", ACCOUNT_COLUMNS), ("sessions", SESSION_COLUMNS), ("saves", SAVE_COLUMNS))] == [1, 1, 1]
    with psycopg.connect(pg_empty) as c:
        c.execute("UPDATE accounts SET presentation = %s", [Jsonb(OLD_ACCOUNT)])
    assert migrate(pg_empty) == head()
    with game_client(pg_empty, monkeypatch) as old:
        old.client.cookies.update(cookies)
        opened = old.client.post(f"/api/saves/{save_id}/open")
        assert opened.status_code == 200, opened.text
        assert opened.json()["presentation"] == {"rule_seen": False, "mix_offered": [], "lessons": [], "lesson_ends": [], "visits": []}
        account = old.client.get("/api/me").json()["account"]
        assert account["settings"] == {"lessons": True}
        assert account["presentation"]["rules_opened"] is True   # control: the account's own keys still read
        assert "lessons" not in account["presentation"]
        assert old.begin()["presentation"]["lessons"] == []   # a new game on that account: nothing kept either
