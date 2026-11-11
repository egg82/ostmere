"""A session is renewed (its last use and its cookie) only by a POST or PUT that succeeds: never by a GET, never by a
refused write (CONTRACT.txt, "Accounts and sessions": a 4xx or 5xx writes nothing)."""
import threading
from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from ashfall_app.accounts.service import PgAccounts
from ashfall_app.api import requestlog
from ashfall_app.db import accounts as account_rows
from ashfall_app.db.tables import sessions
from tests.game_client import GameClient


def last_seen(game: GameClient) -> object:
    with game.app.state.db.engine.connect() as conn:
        return conn.execute(select(sessions.c.last_seen_at)).scalar_one()


def test_only_a_write_that_succeeds_renews_the_session(game: GameClient):
    save = game.begin()["save"]["save_id"]
    began = last_seen(game)
    game.clock.tick(days=2)
    r = game.client.get("/api/me")
    assert r.status_code == 200 and "set-cookie" not in r.headers and last_seen(game) == began
    r = game.advance(save + 99)
    assert r.status_code == 404 and "set-cookie" not in r.headers and last_seen(game) == began
    r = game.decide(save, {"kind": "tap_card", "card": "ghost"}, after=0)
    assert r.status_code == 422 and "set-cookie" not in r.headers and last_seen(game) == began
    r = game.advance(save)
    assert r.status_code == 200 and "__Host-ashfall_session=" in r.headers["set-cookie"]
    assert last_seen(game) == game.clock()
    r = game.advance(save)
    assert r.status_code == 200 and "set-cookie" not in r.headers   # at most once a day


def renewal_fails(*_: object) -> bool:
    raise OperationalError("renew", {}, Exception("the database went away"))


def test_a_renewal_that_fails_changes_nothing_about_the_answer(
        game: GameClient, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    save = game.begin()["save"]["save_id"]
    game.clock.tick(days=2)
    monkeypatch.setattr(PgAccounts, "renew", renewal_fails)
    capsys.readouterr()
    r = game.advance(save)
    assert r.status_code == 200 and "set-cookie" not in r.headers
    line = next(ln for ln in capsys.readouterr().out.splitlines() if "event=session.renew_failed" in ln)
    assert "account=" in line and "level=warning" in line


def test_a_write_reads_its_session_once(game: GameClient, monkeypatch: pytest.MonkeyPatch):
    save = game.begin()["save"]["save_id"]
    reads: list[int] = []
    real: Callable[..., Any] = account_rows.session_by_hash

    def counted(*args: Any, **kwargs: Any) -> Any:
        reads.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(account_rows, "session_by_hash", counted)
    assert game.advance(save).status_code == 200
    assert len(reads) == 1


def test_the_renewal_runs_off_the_event_loop(game: GameClient, monkeypatch: pytest.MonkeyPatch):
    save = game.begin()["save"]["save_id"]
    on_loop: list[int] = []
    renewed_on: list[int] = []
    real: Callable[..., Any] = requestlog.record

    def record(*args: Any, **kwargs: Any) -> Any:   # the route class calls this on the loop
        on_loop.append(threading.get_ident())
        return real(*args, **kwargs)

    def renewing(*_: object) -> bool:
        renewed_on.append(threading.get_ident())
        return False

    monkeypatch.setattr(requestlog, "record", record)
    monkeypatch.setattr(PgAccounts, "renew", renewing)
    assert game.advance(save).status_code == 200
    assert renewed_on and on_loop and renewed_on[0] != on_loop[0]
