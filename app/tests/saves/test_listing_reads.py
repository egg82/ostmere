"""What the saves system reads from the database (asserted on the statements sent, never on time): a listing of an
account's saves selects the columns an Info is made of and never a save's state, and opening a save reads its row once."""
import re
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import Engine, event

from tests.game_client import GameClient


@pytest.fixture
def sent(game: GameClient) -> Iterator[list[str]]:
    statements: list[str] = []

    def record(conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool) -> None:
        statements.append(statement)

    engine: Engine = game.app.state.db.engine
    event.listen(engine, "before_cursor_execute", record)
    yield statements
    event.remove(engine, "before_cursor_execute", record)


_VISIT = re.compile(r"\s*WITH visited AS .*?RETURNING reminder_devices\.id\)\s*", re.S)
"""The reminders' visit stamp, which open and advance fold into their read of the save (db/reminders.py `visit`)."""


def saves_selects(statements: list[str]) -> list[str]:
    bare = (_VISIT.sub("", s, count=1) for s in statements)
    return [s for s in bare if re.match(r"\s*SELECT\b", s) and re.search(r"\bFROM saves\b", s)]


def test_listings_read_no_save_state(game: GameClient, sent: list[str]):
    game.begin()
    keep = game.client.post("/api/saves").json()["save"]["save_id"]
    gone = game.client.post("/api/saves").json()["save"]["save_id"]
    assert game.client.post(f"/api/saves/{gone}/delete").status_code == 200
    sent.clear()
    assert game.client.get("/api/me").json()["saves"]
    assert game.client.get("/api/saves").json()["deleted"], "the listing has a deleted save to read"
    selects = saves_selects(sent)
    assert len(selects) >= 3, "the control: the listings did select from saves"
    assert [s for s in selects if "saves.state" in s] == []
    assert keep != gone


def test_open_reads_the_save_row_once_and_answers_the_values_it_wrote(game: GameClient, sent: list[str]):
    save_id = game.begin()["save"]["save_id"]
    game.clock.tick(600)
    sent.clear()
    r = game.client.post(f"/api/saves/{save_id}/open")
    assert r.status_code == 200
    assert len(saves_selects(sent)) == 1
    shown = r.json()["save"]
    listed = game.client.get("/api/me").json()["saves"][0]
    assert shown == listed, "open's Info is what the list shows after the write"
    assert shown["game_time"] == r.json()["step"]["view"]["at"] and shown["game_time"] > 0
