"""Client reports: logged with exactly the allowed fields, cut to 300 characters, dropped past the rate."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ashfall_app import client_errors, logs
from ashfall_app.main import create_app


SAME_SITE = {"Origin": "https://testserver"}   # every write under /api/ comes from this site (accounts/csrf.py)

def post(client: TestClient, **body: object):
    return client.post("/api/client-errors", json={"kind": "error", "message": "m", **body})


def test_a_report_logs_exactly_the_allowed_fields(capsys: pytest.CaptureFixture[str]):
    client = TestClient(create_app(), headers=SAME_SITE)
    capsys.readouterr()
    r = post(client, source="game.js:10", version="abc", route="/api/saves/{id}/decisions", decision="advance",
             since_begin_s=42, state="STATE-STRING", player_text="hello")
    assert r.status_code == 204
    (line,) = [ln for ln in capsys.readouterr().out.splitlines() if "event=client_error" in ln]
    fields = {p.partition("=")[0] for p in line.split(" ")}
    assert fields == {"ts", "level", "logger", "event", "kind", "message", "source", "version", "route", "decision", "since_begin_s"}
    assert "STATE-STRING" not in line and "hello" not in line and "testclient" not in line.lower()


def test_an_oversized_report_is_truncated(capsys: pytest.CaptureFixture[str]):
    client = TestClient(create_app(), headers=SAME_SITE)
    capsys.readouterr()
    post(client, message="x" * 5000, source="y" * 5000)
    (line,) = [ln for ln in capsys.readouterr().out.splitlines() if "event=client_error" in ln]
    assert "x" * 300 in line and "x" * 301 not in line and "y" * 300 in line and "y" * 301 not in line


def test_leave_is_its_own_event(capsys: pytest.CaptureFixture[str]):
    client = TestClient(create_app(), headers=SAME_SITE)
    capsys.readouterr()
    r = client.post("/api/client-errors", json={
        "kind": "leave", "since_begin_s": 88, "game_time": 120, "last_project": "gather", "decisions": 3, "reached_end": 0})
    assert r.status_code == 204
    out = capsys.readouterr().out
    assert "event=game_leave since_begin_s=88 game_time=120 last_project=gather decisions=3 reached_end=0" in out


def test_a_burst_past_the_rate_is_dropped(capsys: pytest.CaptureFixture[str]):
    now = [0.0]
    gate = client_errors.RateLimit(3, 60.0, clock=lambda: now[0])
    app = FastAPI()
    app.include_router(client_errors.routes(gate))
    logs.setup()
    client = TestClient(app, headers=SAME_SITE)
    capsys.readouterr()
    for _ in range(10):
        assert post(client).status_code == 204
    assert capsys.readouterr().out.count("event=client_error") == 3
    now[0] = 61.0
    post(client)
    assert capsys.readouterr().out.count("event=client_error") == 1
