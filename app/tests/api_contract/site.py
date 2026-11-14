"""Pods and browsers for the blind saves-API contract tests (api/CONTRACT.txt), which reach the app through HTTP only.

A pod is `create_app()` on a test database under a BUILD_VERSION of its own; two pods on one database are two replicas
mid-deploy. A browser is a TestClient on https (the session cookie is Secure, so plain http would never send it back)
that sends this site's Origin, from a client address of its own, and checks that every response it gets names the pod's
build and the app server."""
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from itertools import count
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ashfall_app.main import create_app

SITE = "https://testserver"
COOKIE = "__Host-ashfall_session"
FOUR_HUNDRED_DAYS_S = 400 * 86400
_addresses = count(1)


def fresh_address() -> str:
    """A client address no other browser in this run has (TEST-NET-2), so only the rate tests meet the limit."""
    n = next(_addresses)
    return f"198.51.{100 + n // 250}.{n % 250 + 1}"


@dataclass
class Pod:
    app: FastAPI
    build: str


@contextmanager
def pod(database_url: str | None, build: str) -> Generator[Pod]:
    """A running app on `database_url` (None: no database). Its lifespan runs once, held by a client of its own."""
    with pytest.MonkeyPatch.context() as mp:
        if database_url is None:
            mp.delenv("DATABASE_URL", raising=False)
        else:
            mp.setenv("DATABASE_URL", database_url)
        mp.setenv("BUILD_VERSION", build)
        app = create_app()
        with TestClient(app, base_url=SITE) as warm:
            warm.get("/no-such-route")
            yield Pod(app, build)


def _names_the_build(build: str) -> Callable[[httpx.Response], None]:
    def check(r: httpx.Response) -> None:
        where = f"{r.request.method} {r.request.url.path} -> {r.status_code}"
        assert r.headers.get_list("x-ashfall-build") == [build], f"X-Ashfall-Build on {where}"
        assert r.headers.get_list("x-ashfall-server") == ["app"], f"X-Ashfall-Server on {where}"
    return check


@dataclass
class Browser:
    """One browser on one pod. `cookie` seeds the session (another page of the same browser, or a forged one)."""

    pod: Pod
    address: str = field(default_factory=fresh_address)
    cookie: str | None = None
    origin: str | None = SITE

    def __post_init__(self) -> None:
        headers = {"X-Forwarded-For": self.address}
        if self.origin is not None:
            headers["Origin"] = self.origin
        self.http = TestClient(self.pod.app, base_url=SITE, client=(self.address, 40000), headers=headers,
                               raise_server_exceptions=False)
        if self.cookie is not None:
            self.http.cookies.set(COOKIE, self.cookie)
        self.http.event_hooks = {"request": [], "response": [_names_the_build(self.pod.build)]}

    def session(self) -> str | None:
        return self.http.cookies.get(COOKIE)

    def page_on(self, other: Pod) -> "Browser":
        """Another tab of this browser (same cookie, same address), served by `other`."""
        return Browser(other, self.address, self.session())

    def me(self) -> httpx.Response:
        return self.http.get("/api/me")

    def begin(self) -> httpx.Response:
        return self.http.post("/api/saves")

    def open(self, save_id: object) -> httpx.Response:
        return self.http.post(f"/api/saves/{save_id}/open")

    def advance(self, save_id: object) -> httpx.Response:
        return self.http.post(f"/api/saves/{save_id}/advance")

    def decide(self, save_id: object, decision: dict[str, Any], after: object) -> httpx.Response:
        return self.http.post(f"/api/saves/{save_id}/decisions", json={"decision": decision, "after": after})

    def dry_run(self, save_id: object, decisions: list[dict[str, Any]]) -> httpx.Response:
        return self.http.post(f"/api/saves/{save_id}/dry-run", json={"decisions": decisions})

    def put_me_presentation(self, body: dict[str, Any]) -> httpx.Response:
        return self.http.put("/api/me/presentation", json=body)

    def put_me_settings(self, body: dict[str, Any]) -> httpx.Response:
        return self.http.put("/api/me/settings", json=body)

    def put_save_presentation(self, save_id: object, body: dict[str, Any]) -> httpx.Response:
        return self.http.put(f"/api/saves/{save_id}/presentation", json=body)

    def feedback(self, text: object, save_id: object = None) -> httpx.Response:
        return self.http.post("/api/feedback", json={"text": text} if save_id is None else {"text": text, "save_id": save_id})


def ok(r: httpx.Response) -> dict[str, Any]:
    assert r.status_code == 200, f"{r.request.method} {r.request.url.path}: {r.status_code} {r.text[:300]}"
    body: dict[str, Any] = r.json()
    return body


def refused(r: httpx.Response, status: int, code: str) -> dict[str, Any]:
    """An ApiError {code, message, step}: step is null except on stale."""
    assert r.status_code == status, f"{r.request.method} {r.request.url.path}: {r.status_code} {r.text[:300]}"
    body: dict[str, Any] = r.json()
    assert body.get("code") == code, body
    assert isinstance(body.get("message"), str), body
    assert "step" in body, body
    if code != "stale":
        assert body["step"] is None, body
    return body


def account_of(rules_opened: bool = False, devices_opened: bool = False, lessons: bool = True) -> dict[str, Any]:
    """An Account with no recovery words and none due, holding this presentation and the lessons setting."""
    return {"presentation": {"rules_opened": rules_opened, "devices_opened": devices_opened,
                             "reminder_mentioned": False, "ledger_lines": [], "mix_stopped": [], "switch_offered": [], "journal_read": []},
            "settings": {"lessons": lessons}, "has_words": False, "words_due": False}


def save_presentation_of(rule_seen: bool = False, lessons: list[str] | None = None) -> dict[str, Any]:
    """A SavePresentation with these flags, no dots touched and no lesson ends."""
    return {"rule_seen": rule_seen, "mix_offered": [], "lessons": lessons or [], "lesson_ends": [], "visits": [], "chapter": None}


def begun(b: Browser) -> tuple[Any, dict[str, Any]]:
    """Begin: (save_id, first Step)."""
    new = ok(b.begin())
    return new["save"]["save_id"], new["step"]


SET_NO_ORDERS: dict[str, Any] = {"kind": "set_orders", "orders": []}
"""A decision valid on any save: the player's rules, emptied."""


def ready_tap(view: dict[str, Any]) -> dict[str, Any] | None:
    """A tap the view says is ready now: a card with no blocker while every lane is free (CONTRACT, "can be tapped
    iff"; the card's lane is in Content, so this asks for all of them)."""
    if any(lane["running_card"] is not None for lane in view["lanes"]):
        return None
    card = next((c for c in view["cards"] if c["blocker"] is None), None)
    return None if card is None else {"kind": "tap_card", "card": card["card"]}


def busy_tap(view: dict[str, Any]) -> dict[str, Any] | None:
    """A tap of the card a lane is running now: a busy lane, refused (422 invalid_decision)."""
    running = next((lane["running_card"] for lane in view["lanes"] if lane["running_card"] is not None), None)
    return None if running is None else {"kind": "tap_card", "card": running}
