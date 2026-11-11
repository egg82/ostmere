"""The API logs one line per request with the allowed fields, and no line anywhere carries a cookie, a session token, the
client's address, the rate key or a save's state (logs.py: ids and counts only). The second test plants each of them
and looks for it in everything the app wrote."""
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from ashfall_app.accounts.cookies import SESSION
from ashfall_app import logs
from ashfall_app.api.requestlog import Asked, failed_tap
from ashfall_app.db.tables import saves
from ashfall_app.main import create_app
from tests.game_client import RATE_KEY, SITE, GameClient

ADDRESS = "203.0.113.77"


def request_lines(out: str) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for ln in out.splitlines():
        if "event=game.request" in ln:
            found.append({k: v for k, _, v in (p.partition("=") for p in ln.split(" "))})
    return found


def test_each_route_logs_its_fields(game: GameClient, capsys: pytest.CaptureFixture[str]):
    capsys.readouterr()
    assert game.client.get("/api/content").status_code == 200
    made = game.begin()
    save = made["save"]["save_id"]
    card = next(c["card"] for c in made["step"]["view"]["cards"] if c["blocker"] is None)
    game.clock.tick(5)
    headers = {"X-Ashfall-Wall": "12", "X-Ashfall-Gap": "7"}
    r = game.client.post(f"/api/saves/{save}/decisions", headers=headers,
                         json={"decision": {"kind": "tap_card", "card": card}, "after": 0})
    assert r.status_code == 200
    stale = game.decide(save, {"kind": "tap_card", "card": card}, after=0)
    assert stale.status_code == 409
    content, created, decided, refused = request_lines(capsys.readouterr().out)
    assert content["route"] == "/api/content" and content["status"] == "200" and "save" not in content
    assert created["route"] == "/api/saves" and created["status"] == "200"
    assert decided["route"] == "/api/saves/{save_id}/decisions" and decided["save"] == str(save)
    assert decided["decision"] == "tap_card" and decided["target"] == card and decided["after"] == "0"
    assert decided["wall_s"] == "12" and decided["gap_s"] == "7" and decided["failed"] == "0" and "ms" in decided
    assert refused["status"] == "409" and refused["error"] == "stale"


def test_failed_is_the_answers_failed_tap():
    """failed=1 when the Step names the tapped card as a failed tap; 0 for another card or none; no field for a
    decision that is not a tap."""
    tap = Asked("tap_card", "c", 0)
    assert failed_tap(tap, b'{"failed_tap": "c"}') == 1
    assert failed_tap(tap, b'{"failed_tap": "d"}') == failed_tap(tap, b'{"failed_tap": null}') == 0
    assert failed_tap(Asked("set_orders", None, 0), b'{"failed_tap": null}') is None


def test_no_line_carries_a_cookie_token_address_key_or_state(pg_url: str, monkeypatch: pytest.MonkeyPatch,
                                                            capsys: pytest.CaptureFixture[str]):
    monkeypatch.setenv("DATABASE_URL", pg_url)
    monkeypatch.setenv("ASHFALL_RATE_KEY", RATE_KEY)
    app = create_app()
    with TestClient(app, base_url=SITE, client=(ADDRESS, 50000), headers={"Origin": SITE}) as client:
        made = client.post("/api/saves").json()
        save = made["save"]["save_id"]
        token = client.cookies[SESSION]
        client.post(f"/api/saves/{save}/decisions", json={"decision": {"kind": "tap_card", "card": "stand_up"}, "after": 0})
        client.post(f"/api/saves/{save}/open")
        client.post(f"/api/saves/{save}/decisions", json={"decision": {"kind": "tap_card", "card": "ghost"}, "after": 9})
        client.get("/api/me")
        with app.state.db.engine.connect() as conn:
            state = conn.execute(select(saves.c.state)).scalar_one()
    out = capsys.readouterr().out
    assert "event=account.created" in out and "event=save.decision" in out and "event=game.request" in out
    assert len(token) >= 40 and len(state) > 200   # control: the planted values are real and long
    for planted in (token, ADDRESS, RATE_KEY, state, state[:60], state[-60:]):
        assert planted not in out, planted[:20]


def test_start_logs_the_rules_digest(capsys: pytest.CaptureFixture[str]):
    digest = TestClient(create_app()).get("/api/content").json()["rules_digest"]
    assert f"event=app.start rules={digest}" in capsys.readouterr().out


def test_a_lesson_end_is_logged_once_with_ids_and_seconds(game: GameClient, capsys: pytest.CaptureFixture[str]):
    save = game.begin()["save"]["save_id"]
    end = {"lesson": "first_mix", "skipped": True, "step": 2, "longest_wait_s": 41}
    capsys.readouterr()
    for _ in range(2):   # the page sends the whole presentation at every change: the same end is one line
        r = game.client.put(f"/api/saves/{save}/presentation", json={"lessons": ["first_mix"], "lesson_ends": [end]})
        assert r.status_code == 200 and r.json()["lesson_ends"] == [end]
    lines = [ln for ln in capsys.readouterr().out.splitlines() if "event=lesson.end" in ln]
    assert len(lines) == 1
    assert lines[0].endswith(f"save={save} lesson=first_mix outcome=skipped step=2 longest_wait_s=41")


def test_a_mix_name_is_logged_only_as_a_short_hash(game: GameClient, capsys: pytest.CaptureFixture[str]):
    name = "Zebra Pie Morning"
    save = game.begin()["save"]["save_id"]
    capsys.readouterr()
    mix: dict[str, Any] = {"id": name, "components": []}
    decisions: list[dict[str, Any]] = [{"kind": "save_mix", "mix": mix}, {"kind": "switch_mix", "mix_id": name},
                                       {"kind": "delete_mix", "mix_id": name}]
    for decision in decisions:
        game.client.post(f"/api/saves/{save}/decisions", json={"decision": decision, "after": 0})
    out = capsys.readouterr().out
    mine = [ln for ln in out.splitlines() if "event=save.decision" in ln and "kind=switch_mix" in ln]
    assert mine and f"target={logs.tag(name)}" in mine[0], "control: the decision is logged, with the hash"   # the hash stands in for the name
    assert name not in out and "Zebra" not in out
