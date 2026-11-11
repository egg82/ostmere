"""Two pages of one account keep what the account's presentation, and each save's, has grown to, however stale the
second one's copy is (api/CONTRACT.txt, AccountPresentation and SavePresentation): a PUT adds to what is stored, never
takes away, and each lesson end is logged once for its save."""
from typing import Any

import pytest

from ashfall_app.accounts.presentation import NEWEST, merge_presentation
from ashfall_app.accounts.interface import Json
from ashfall_app.api.limits import MAX_VISITS
from tests.game_client import GameClient


def end(lesson: str, skipped: bool = False) -> dict[str, Any]:
    return {"lesson": lesson, "skipped": skipped, "step": 1, "longest_wait_s": 3}


def put(game: GameClient, body: dict[str, Any]) -> dict[str, Any]:
    r = game.client.put("/api/me/presentation", json=body)
    assert r.status_code == 200, r.text
    found: dict[str, Any] = r.json()["presentation"]
    return found


def put_save(game: GameClient, save_id: int, body: dict[str, Any]) -> dict[str, Any]:
    r = game.client.put(f"/api/saves/{save_id}/presentation", json=body)
    assert r.status_code == 200, r.text
    found: dict[str, Any] = r.json()
    return found


def lines(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return [ln for ln in capsys.readouterr().out.splitlines() if "event=lesson.end" in ln]


def test_a_stale_page_does_not_erase_what_another_page_kept(game: GameClient, capsys: pytest.CaptureFixture[str]):
    save = game.begin()["save"]["save_id"]
    capsys.readouterr()
    put_save(game, save, {"lessons": ["first_mix"], "lesson_ends": [end("first_mix")]})
    put_save(game, save, {"mix_offered": ["wood"]})   # tab B, opened before tab A kept anything
    mine = put_save(game, save, {"lessons": ["first_mix"], "lesson_ends": [end("first_mix")]})
    assert mine["lessons"] == ["first_mix"] and mine["mix_offered"] == ["wood"]
    assert game.client.post(f"/api/saves/{save}/open").json()["presentation"] == mine
    logged = lines(capsys)
    assert len(logged) == 1 and f"save={save}" in logged[0]
    put(game, {"rules_opened": True})
    account = put(game, {"ledger_lines": ["wood"]})
    assert account["rules_opened"] is True and account["ledger_lines"] == ["wood"]
    assert game.client.get("/api/me").json()["account"]["presentation"] == account


def test_the_answer_is_the_merged_presentation(game: GameClient):
    save = game.begin()["save"]["save_id"]
    put(game, {"switch_offered": [{"chip": "c", "mix_id": "m"}], "rules_opened": True})
    got = put(game, {"switch_offered": [{"chip": "c", "mix_id": "m"}]})
    assert got["switch_offered"] == [{"chip": "c", "mix_id": "m"}] and got["rules_opened"] is True
    put_save(game, save, {"mix_offered": ["a"], "rule_seen": True})
    kept = put_save(game, save, {"mix_offered": ["b"]})
    assert kept["mix_offered"] == ["a", "b"] and kept["rule_seen"] is True


def test_two_alternating_full_sets_of_lessons_log_each_lesson_once(game: GameClient, capsys: pytest.CaptureFixture[str]):
    save = game.begin()["save"]["save_id"]
    capsys.readouterr()
    a = {"lessons": [f"a{n}" for n in range(512)], "lesson_ends": [end(f"a{n}") for n in range(512)]}
    b = {"lessons": [f"b{n}" for n in range(512)], "lesson_ends": [end(f"b{n}") for n in range(512)]}
    for body in (a, b, a, b, a):
        got = put_save(game, save, body)
        assert len(got["lessons"]) <= 512 and len(got["lesson_ends"]) <= 512
    logged = [ln.split("lesson=")[1].split(" ")[0] for ln in lines(capsys)]
    assert len(logged) > 0 and len(logged) == len(set(logged))


def test_a_new_save_keeps_no_lesson_another_save_kept(game: GameClient):
    """Lessons are per save: a second game of the account starts with nothing kept about its teaching."""
    first = game.begin()
    assert first["presentation"] == {"rule_seen": False, "mix_offered": [], "lessons": [], "lesson_ends": [], "visits": []}
    put_save(game, first["save"]["save_id"], {"lessons": ["first_mix", "first_rule"], "rule_seen": True,
                                              "lesson_ends": [end("first_mix"), end("first_rule")]})
    second = game.begin()
    assert second["presentation"]["lessons"] == [] and second["presentation"]["rule_seen"] is False
    opened = game.client.post(f"/api/saves/{second['save']['save_id']}/open").json()
    assert opened["presentation"]["lessons"] == []
    again = game.client.post(f"/api/saves/{first['save']['save_id']}/open").json()   # control: the first keeps its own
    assert again["presentation"]["lessons"] == ["first_mix", "first_rule"]


def test_a_save_presentation_is_the_owners_alone(game: GameClient):
    """Another account's save, a save that does not exist and a deleted save are all 404, and nothing is written."""
    mine = game.begin()["save"]["save_id"]
    stranger = game.stranger()
    assert stranger.post("/api/saves").status_code == 200
    r = stranger.put(f"/api/saves/{mine}/presentation", json={"lessons": ["first_mix"]})
    assert r.status_code == 404, r.text
    assert game.client.put("/api/saves/999999/presentation", json={"lessons": ["x"]}).status_code == 404
    assert game.client.post(f"/api/saves/{mine}/open").json()["presentation"]["lessons"] == []
    other = game.begin()["save"]["save_id"]   # an account keeps its last live save, so delete a second one
    assert game.client.post(f"/api/saves/{other}/delete").status_code == 200
    assert game.client.put(f"/api/saves/{other}/presentation", json={"lessons": ["x"]}).status_code == 404


def test_lessons_setting_defaults_on_and_turns_off_and_back(game: GameClient):
    game.begin()
    assert game.client.get("/api/me").json()["account"]["settings"] == {"lessons": True}
    r = game.client.put("/api/me/settings", json={"lessons": False})
    assert r.status_code == 200, r.text
    assert r.json()["settings"] == {"lessons": False}
    assert game.client.get("/api/me").json()["account"]["settings"] == {"lessons": False}
    assert game.client.put("/api/me/settings", json={"lessons": True}).json()["settings"] == {"lessons": True}
    assert game.stranger().put("/api/me/settings", json={"lessons": False}).status_code == 401
    assert game.client.put("/api/me/settings", json={"lessons": False, "other": 1}).status_code == 422


def visit(n: int) -> dict[str, object]:
    return {"left": n * 10, "back": n * 10 + 5}


def visits(first: int, stop: int) -> Json:
    return {"visits": [visit(n) for n in range(first, stop)]}


def test_visits_keep_the_newest_and_drop_the_oldest():
    limit = NEWEST["visits"]
    kept = merge_presentation(visits(0, limit), visits(limit, limit + 3), 512)["visits"]
    assert kept == visits(3, limit + 3)["visits"]


def test_visits_within_the_limit_all_stay():
    assert merge_presentation(visits(1, 2), visits(2, 3), 512) == visits(1, 3)


def test_a_stored_list_over_the_limit_is_trimmed_not_refused():
    over = NEWEST["visits"] + 5
    assert merge_presentation(visits(0, over), visits(over, over + 1), 512) == visits(6, over + 1)


def test_the_limit_is_the_api_s_visit_limit():
    assert NEWEST["visits"] == MAX_VISITS
