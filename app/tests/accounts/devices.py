"""The app with a join key, a rate key and a clock the test moves, and browsers on it: the implementation tests of
moving to another device (test_devices_*.py) drive it over HTTP and read the database behind it."""
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from itertools import count
from typing import Any

import httpx
import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import NullPool

from ashfall_app.main import create_app
from tests.fake_clock import FakeClock

SITE = "https://testserver"
JOIN_KEY = bytes(range(32))
COOKIE = "__Host-ashfall_session"
_addresses = count(1)


@dataclass
class Site:
    app: FastAPI
    clock: FakeClock
    db: Engine

    def scalar(self, query: str, **params: object) -> Any:
        with self.db.connect() as c:
            return c.execute(text(query), params).scalar()

    def run(self, query: str, **params: object) -> None:
        with self.db.begin() as c:
            c.execute(text(query), params)


@dataclass
class Browser:
    site: Site
    address: str = field(default_factory=lambda: f"192.0.2.{next(_addresses) % 250 + 1}")

    def __post_init__(self) -> None:
        self.http = TestClient(self.site.app, base_url=SITE, client=(self.address, 40000), headers={"Origin": SITE},
                               raise_server_exceptions=False)

    def session(self) -> str | None:
        return self.http.cookies.get(COOKIE)

    def begin(self) -> dict[str, Any]:
        r = self.http.post("/api/saves")
        assert r.status_code == 200, r.text
        found: dict[str, Any] = r.json()
        return found

    def play(self) -> int:
        """Begins a game and decides once in it (progress); the save's id."""
        new = self.begin()
        save_id: int = new["save"]["save_id"]
        r = self.http.post(f"/api/saves/{save_id}/decisions",
                           json={"decision": {"kind": "set_orders", "orders": []}, "after": 0})
        assert r.status_code == 200, r.text
        return save_id

    def me(self) -> dict[str, Any]:
        found: dict[str, Any] = self.http.get("/api/me").json()
        return found

    def code(self) -> httpx.Response:
        return self.http.post("/api/me/transfer-code")

    def words(self) -> httpx.Response:
        return self.http.post("/api/me/words")

    def join(self, typed: str, merge: bool = False, keep: bool = False) -> httpx.Response:
        return self.http.post("/api/join", json={"typed": typed, "merge": merge, "keep": keep})


@contextmanager
def site(pg_url: str, monkeypatch: pytest.MonkeyPatch, join_key: str | None = JOIN_KEY.hex()) -> Generator[Site]:
    monkeypatch.setenv("DATABASE_URL", pg_url)
    monkeypatch.setenv("ASHFALL_RATE_KEY", "devices-rate-key")
    if join_key is None:
        monkeypatch.delenv("ASHFALL_JOIN_KEY", raising=False)
    else:
        monkeypatch.setenv("ASHFALL_JOIN_KEY", join_key)
    clock = FakeClock()
    app = create_app(clock)
    db = create_engine("postgresql+psycopg://", creator=lambda: psycopg.connect(pg_url), poolclass=NullPool)
    with TestClient(app, base_url=SITE):
        yield Site(app, clock, db)
    db.dispose()


def code_of(r: httpx.Response) -> str:
    assert r.status_code == 200, r.text
    found: str = r.json()["transfer_code"]
    return found
