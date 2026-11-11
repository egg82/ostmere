"""PUT and DELETE /api/reminders (CONTRACT.txt, "Reminders") through the app, on a database of the test's own."""
import pytest

from tests.game_client import GameClient
from tests.reminders.wire import PUSH, WINDOW, on, rows


def test_put_turns_reminders_on_and_answers_the_window(game: GameClient):
    game.begin()
    r = game.client.put("/api/reminders", json=on())
    assert r.status_code == 200, r.text
    assert r.json() == {"window": WINDOW}
    assert r.headers["cache-control"] == "no-store"
    [row] = rows(game)
    assert (row["endpoint"], row["tz"], row["after_hours"], row["send_from_hour"], row["send_until_hour"]) == (
        PUSH + "one", "Europe/Paris", 24, 9, 21)


def test_a_second_put_changes_the_window_and_keeps_one_row(game: GameClient):
    game.begin()
    game.client.put("/api/reminders", json=on())
    wraps = {"after_hours": 168, "send_from_hour": 22, "send_until_hour": 7}
    assert game.client.put("/api/reminders", json=on(window=wraps)).json() == {"window": wraps}
    assert [(x["after_hours"], x["send_from_hour"], x["send_until_hour"]) for x in rows(game)] == [(168, 22, 7)]


def test_a_put_without_a_window_refreshes_keys_and_answers_the_stored_window(game: GameClient):
    game.begin()
    game.client.put("/api/reminders", json=on())
    fresh = on(window=None, tz="America/New_York") | {"p256dh": "BNew-key"}
    r = game.client.put("/api/reminders", json=fresh)
    assert r.status_code == 200, r.text
    assert r.json() == {"window": WINDOW}
    [row] = rows(game)
    assert (row["p256dh"], row["tz"]) == ("BNew-key", "America/New_York")


def test_a_put_without_a_window_for_a_browser_not_on_is_404_and_stores_nothing(game: GameClient):
    game.begin()
    r = game.client.put("/api/reminders", json=on(window=None))
    assert r.status_code == 404 and r.json()["code"] == "not_found"
    assert rows(game) == []


def test_a_refresh_moves_the_row_to_the_account_the_browser_now_holds(game: GameClient):
    game.begin()
    game.client.put("/api/reminders", json=on())
    [was] = rows(game)
    other = game.stranger()
    assert other.post("/api/saves").status_code == 200
    assert other.put("/api/reminders", json=on(window=None)).status_code == 200
    [now] = rows(game)
    assert now["account_id"] != was["account_id"]


def test_put_refuses_what_does_not_fit(game: GameClient):
    game.begin()
    refused = [
        on(endpoint="https://example.com/push"),
        on(endpoint="http://fcm.googleapis.com/fcm/send/x"),
        on(tz="Mars/Olympus"),
        on(window=WINDOW | {"after_hours": 5}),
        on(window=WINDOW | {"send_until_hour": 24}),
        on() | {"surprise": 1},
    ]
    for body in refused:
        r = game.client.put("/api/reminders", json=body)
        assert r.status_code == 422 and r.json()["code"] == "invalid_decision", (body, r.text)
    assert rows(game) == []


def test_put_without_an_account_is_401(game: GameClient):
    r = game.stranger().put("/api/reminders", json=on())
    assert r.status_code == 401 and r.json()["code"] == "no_account"


def test_delete_turns_reminders_off(game: GameClient):
    game.begin()
    game.client.put("/api/reminders", json=on())
    r = game.client.request("DELETE", "/api/reminders", json={"endpoint": PUSH + "one"})
    assert r.status_code == 204, r.text
    assert rows(game) == []
    assert game.client.request("DELETE", "/api/reminders", json={"endpoint": PUSH + "one"}).status_code == 204


def test_delete_leaves_another_accounts_row(game: GameClient):
    game.begin()
    game.client.put("/api/reminders", json=on())
    other = game.stranger()
    assert other.post("/api/saves").status_code == 200
    assert other.request("DELETE", "/api/reminders", json={"endpoint": PUSH + "one"}).status_code == 204
    assert len(rows(game)) == 1


def test_the_endpoint_is_never_logged(game: GameClient, capsys: pytest.CaptureFixture[str]):
    game.begin()
    game.client.put("/api/reminders", json=on())
    game.client.request("DELETE", "/api/reminders", json={"endpoint": PUSH + "one"})
    out = capsys.readouterr()
    assert "reminder.kept" in out.out + out.err
    assert PUSH not in out.out + out.err and "BPk-key" not in out.out + out.err
