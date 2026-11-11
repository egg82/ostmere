"""The app on a database of the test's own, with a clock the test moves, behind a TestClient that keeps cookies
(https, so the Secure session cookie comes back). `begin()` signs in the way a browser does: POST /api/saves."""
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ashfall_app.main import create_app
from tests.fake_clock import FakeClock

Json = dict[str, Any]
RATE_KEY = "test-rate-key"
SITE = "https://testserver"


class GameClient:
    def __init__(self, app: FastAPI, client: TestClient, clock: FakeClock) -> None:
        self.app, self.client, self.clock = app, client, clock

    def begin(self) -> Json:
        """A new save (and the account, on a browser with none); the NewSave."""
        r = self.client.post("/api/saves")
        assert r.status_code == 200, r.text
        found: Json = r.json()
        return found

    def decide(self, save_id: int, decision: Json, after: int) -> Any:
        return self.client.post(f"/api/saves/{save_id}/decisions", json={"decision": decision, "after": after})

    def advance(self, save_id: int) -> Any:
        return self.client.post(f"/api/saves/{save_id}/advance")

    def stranger(self) -> TestClient:
        """Another browser on the same app: no cookies."""
        return TestClient(self.app, base_url=SITE, headers={"Origin": SITE})


@contextmanager
def game_client(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Generator[GameClient]:
    monkeypatch.setenv("DATABASE_URL", pg_url)
    monkeypatch.setenv("ASHFALL_RATE_KEY", RATE_KEY)
    clock = FakeClock()
    app = create_app(clock)
    with TestClient(app, base_url=SITE, headers={"Origin": SITE}) as client:
        yield GameClient(app, client, clock)
