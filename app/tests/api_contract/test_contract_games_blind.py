# Blind contract tests for several saves on one account (CONTRACT.txt, GAMES ON ONE ACCOUNT), written from the contract,
# the openapi models and the harness (site.py, rows.py) only.
#
# Ambiguities in the contract, each tested on the stricter reading:
#  1. "the current one": the contract names none; read as the first of Games.saves (most recently played), which is what
#     a new game must switch to.
#  2. camp_level "null for one not written since the build before this field": read as an int on every save written
#     now, a new one included (0 <= level <= len(Content.camp.camp_levels)).
#  3. "number ... the highest number the account holds (deleted saves included) plus one": read so that a purged save
#     stops counting, but a merely deleted one does not; a restore keeps the number.
#  4. A deleted save "answers as for a save that does not exist": read as the same status, code, step and merge (the
#     message is for the console and names the id); feedback is 204 either way, with the save_id not kept.
#  5. Delete/restore with no account: 401 no_account (the table lists 401 for GET /api/saves only).
#  6. Purge "may be gone for good" after purge_at, "a small batch at a time": read as gone after the next delete or new
#     game on any account, for one save; and not gone before purge_at.
#  7. The 10-a-day limit "beyond its first save": read as 10 new games after the first are allowed, the 11th refused;
#     a refusal (cap or limit) makes no save; a restore does not count.
#  8. The 24-hour window is reached through the rows (saves' and tries' timestamps), as the contract names no clock.
#  9. A write with a body that is not JSON: 415 not_json even on delete/restore, which take no body; a write with no body
#     at all is accepted.
# 10. "A join moves an account with all its saves": read through the browser that joins seeing the other account's live
#     and deleted saves, with the joining browser's own empty-of-decisions account gone.
import os
from datetime import datetime, timedelta
from typing import Any

import httpx
import psycopg
import pytest

from tests.api_contract import rows
from tests.api_contract.site import Browser, Pod, begun, ok, refused

MISSING = 987654321


@pytest.fixture(autouse=True)
def join_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASHFALL_JOIN_KEY", os.urandom(32).hex())


def games(b: Browser) -> dict[str, Any]:
    return ok(b.http.get("/api/saves"))


def delete(b: Browser, save_id: object) -> httpx.Response:
    return b.http.post(f"/api/saves/{save_id}/delete")


def restore(b: Browser, save_id: object) -> httpx.Response:
    return b.http.post(f"/api/saves/{save_id}/restore")


def ids(saves: list[dict[str, Any]]) -> list[Any]:
    return [s["save_id"] for s in saves]


def when(text: str) -> datetime:
    t = datetime.fromisoformat(text.replace("Z", "+00:00"))
    assert t.tzinfo is not None and t.utcoffset() == timedelta(0), f"not UTC: {text}"
    return t


def account_with(pod_a: Pod, n: int) -> tuple[Browser, list[Any]]:
    """A browser on an account holding n live saves, oldest first."""
    b = Browser(pod_a)
    made = [begun(b)[0] for _ in range(n)]
    return b, made


def same_as_missing(r: httpx.Response, missing: httpx.Response) -> None:
    def shape(x: httpx.Response) -> tuple[int, Any, Any, Any]:   # the message is for the console, so not compared
        body = x.json()
        return x.status_code, body["code"], body["step"], body["merge"]
    assert shape(r) == shape(missing), (r.request.url.path, r.text)


def test_the_list_shape_numbers_and_times(pod_a: Pod):
    b = Browser(pod_a)
    first, _ = begun(b)
    g = games(b)
    assert set(g) == {"saves", "deleted", "max_saves", "kept_days"}
    assert (g["max_saves"], g["kept_days"], g["deleted"]) == (5, 30, [])
    assert ids(g["saves"]) == [first]
    s = g["saves"][0]
    assert s["number"] == 1
    assert (s["decisions"], s["game_time"], s["ended_at"]) == (0, 0, None)
    assert when(s["started_at"]) <= when(s["played_at"])
    levels = len(ok(b.http.get("/api/content"))["camp"]["camp_levels"])
    assert isinstance(s["camp_level"], int) and 0 <= s["camp_level"] <= levels, s["camp_level"]
    assert g["saves"] == ok(b.me())["saves"]


def test_played_at_moves_on_a_write_and_started_at_does_not(pod_a: Pod):
    b, (one, two) = account_with(pod_a, 2)
    before = {s["save_id"]: s for s in games(b)["saves"]}
    assert ids(games(b)["saves"]) == [two, one]
    ok(b.advance(one))
    after = games(b)["saves"]
    assert ids(after) == [one, two]
    by = {s["save_id"]: s for s in after}
    assert by[one]["started_at"] == before[one]["started_at"]
    assert when(by[one]["played_at"]) > when(before[one]["played_at"])
    assert by[two] == before[two]
    assert by[one]["number"] == 1 and by[two]["number"] == 2


def test_a_new_game_keeps_the_others_and_is_the_current_one(pod_a: Pod):
    b, (one, two) = account_with(pod_a, 2)
    kept = {s["save_id"]: s for s in games(b)["saves"]}
    new, step = begun(b)
    g = games(b)
    assert ids(g["saves"]) == [new, two, one]
    assert [s["number"] for s in g["saves"]] == [3, 2, 1]
    assert step["save_id"] == new
    for sid in (one, two):
        assert {s["save_id"]: s for s in g["saves"]}[sid] == kept[sid]
    assert ids(ok(b.me())["saves"]) == [new, two, one]
    ok(b.advance(one))
    ok(b.advance(two))


def test_numbers_count_deleted_saves_and_a_restore_keeps_its_number(pod_a: Pod):
    b, (one, two, three) = account_with(pod_a, 3)
    delete(b, three)
    fourth, _ = begun(b)
    assert {s["save_id"]: s["number"] for s in games(b)["saves"]} == {one: 1, two: 2, fourth: 4}
    ok(restore(b, three))
    assert {s["save_id"]: s["number"] for s in games(b)["saves"]}[three] == 3


def test_the_cap_refuses_a_sixth_live_save_and_makes_nothing(pod_a: Pod):
    b, made = account_with(pod_a, 5)
    before = games(b)
    r = b.begin()
    refused(r, 409, "too_many_saves")
    assert games(b) == before
    ok(delete(b, made[0]))   # deleted saves do not count
    ok(b.begin())
    assert len(games(b)["saves"]) == 5


@pytest.fixture
def browser_ten_games_in(pod_a: Pod) -> Browser:
    """A browser that has begun eleven games today (the cap of live saves held by deleting the last), in setup."""
    b = Browser(pod_a)
    begun(b)
    for _ in range(10):   # ten beyond the first save
        live = games(b)["saves"]
        if len(live) == 5:
            ok(delete(b, live[-1]["save_id"]))
        ok(b.begin())
    return b


def test_the_daily_limit_on_new_games(pg_url: str, browser_ten_games_in: Browser):
    b = browser_ten_games_in
    live = games(b)["saves"]
    if len(live) == 5:
        ok(delete(b, live[-1]["save_id"]))
    before = games(b)
    r = b.begin()
    refused(r, 429, "rate_limited")
    retry = r.headers.get("retry-after")
    assert retry is not None and retry.isdigit() and int(retry) > 0, retry
    assert games(b) == before
    ok(restore(b, before["deleted"][0]["save"]["save_id"]))   # a restore is not a new game
    # a day on, the window has moved
    rows.run(pg_url, "UPDATE tries SET at = at - interval '25 hours'")
    rows.run(pg_url, "UPDATE saves SET created_at = created_at - interval '25 hours', "
                     "started_at = started_at - interval '25 hours'")
    ok(delete(b, games(b)["saves"][-1]["save_id"]))
    ok(b.begin())


def test_delete_hides_the_save_everywhere_until_restored(pg_url: str, pod_a: Pod):
    b, (one, two) = account_with(pod_a, 2)
    info = {s["save_id"]: s for s in games(b)["saves"]}[one]
    g = ok(delete(b, one))
    assert ids(g["saves"]) == [two]
    assert [d["save"]["save_id"] for d in g["deleted"]] == [one]
    assert g == games(b)
    assert ids(ok(b.me())["saves"]) == [two]
    missing = b.advance(MISSING)
    refused(missing, 404, "not_found")
    calls = [b.open(one), b.advance(one), b.decide(one, {"kind": "set_orders", "orders": []}, 0),
             b.http.post(f"/api/saves/{one}/forecast"), b.dry_run(one, [])]
    for r, probe in zip(calls, [b.open(MISSING), b.advance(MISSING), b.decide(MISSING, {"kind": "set_orders", "orders": []}, 0),
                                b.http.post(f"/api/saves/{MISSING}/forecast"), b.dry_run(MISSING, [])]):
        same_as_missing(r, probe)
        assert r.status_code == 404
    # feedback is 204 and keeps a save_id only for a save the account owns (live): a deleted one is not kept
    assert b.feedback("hello", one).status_code == 204
    assert rows.scalar(pg_url, "SELECT save_id FROM feedback ORDER BY id DESC LIMIT 1") is None
    again = ok(restore(b, one))
    assert ids(again["saves"]) == [one, two] or ids(again["saves"]) == [two, one]
    assert again["deleted"] == []
    back = {s["save_id"]: s for s in again["saves"]}[one]
    for k in ("number", "decisions", "game_time", "started_at", "camp_level", "ended_at"):
        assert back[k] == info[k], k
    ok(b.advance(one))


def test_a_held_save_lists_when_it_was_deleted_and_when_it_may_go(pod_a: Pod):
    b, (one, _, three) = account_with(pod_a, 3)
    ok(delete(b, one))
    ok(delete(b, three))
    held = games(b)["deleted"]
    assert [d["save"]["save_id"] for d in held] == [three, one]   # most recently deleted first
    for d in held:
        assert when(d["purge_at"]) - when(d["deleted_at"]) == timedelta(days=30)
    assert when(held[0]["deleted_at"]) >= when(held[1]["deleted_at"])
    assert delete(b, one).status_code == 404   # already deleted: no live save of that id
    refused(delete(b, MISSING), 404, "not_found")


def test_the_last_live_save_cannot_be_deleted(pod_a: Pod):
    b, (one, two) = account_with(pod_a, 2)
    ok(delete(b, two))
    before = games(b)
    refused(delete(b, one), 409, "last_save")
    assert games(b) == before
    ok(b.advance(one))
    ok(restore(b, two))
    ok(delete(b, one))   # two lives again, so one is no longer the only one


def test_restore_at_the_cap_is_409_and_changes_nothing(pod_a: Pod):
    b, made = account_with(pod_a, 5)
    ok(delete(b, made[0]))
    ok(b.begin())
    before = games(b)
    assert len(before["saves"]) == 5
    refused(restore(b, made[0]), 409, "too_many_saves")
    assert games(b) == before


def test_restore_of_a_live_or_unknown_save_is_404(pod_a: Pod):
    b, (one, _) = account_with(pod_a, 2)
    refused(restore(b, one), 404, "not_found")
    refused(restore(b, MISSING), 404, "not_found")


def test_no_account_is_401_on_the_games_routes(pod_a: Pod):
    b = Browser(pod_a)
    refused(b.http.get("/api/saves"), 401, "no_account")
    refused(delete(b, 1), 401, "no_account")
    refused(restore(b, 1), 401, "no_account")


def held_columns(url: str) -> list[str]:
    with psycopg.connect(url) as c:
        found = c.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'saves' "
                          "AND column_name IN ('deleted_at', 'purge_at')").fetchall()
    return [r[0] for r in found]


def age_deleted(url: str, days: int) -> None:
    cols = held_columns(url)
    if "deleted_at" not in cols:
        pytest.skip("the contract names no clock for a deletion and the saves table has no deleted_at column to move")
    query = ("UPDATE saves SET deleted_at = deleted_at - make_interval(days => %s), "
             "purge_at = purge_at - make_interval(days => %s) WHERE deleted_at IS NOT NULL"
             if "purge_at" in cols else
             "UPDATE saves SET deleted_at = deleted_at - make_interval(days => %s) WHERE deleted_at IS NOT NULL")
    assert rows.run(url, query, *([days, days] if "purge_at" in cols else [days])) > 0


def test_a_deleted_save_is_purged_only_after_purge_at_by_the_next_delete_or_new_game(pg_url: str, pod_a: Pod):
    b, (one, two, _three) = account_with(pod_a, 3)
    ok(delete(b, one))
    ok(delete(b, two))
    saves_before = rows.count(pg_url, "saves")   # 3, deleted ones still rows
    age_deleted(pg_url, 29)
    ok(b.begin())   # before purge_at: held
    assert sorted(d["save"]["save_id"] for d in games(b)["deleted"]) == sorted([one, two])
    assert rows.count(pg_url, "saves") == saves_before + 1
    age_deleted(pg_url, 2)   # now past purge_at, but nothing has run
    other = Browser(pod_a)
    ok(other.begin())   # a new game on any account purges
    assert games(b)["deleted"] == []
    assert rows.count(pg_url, "saves") == saves_before + 2 - 2   # two purged, two begun since
    refused(restore(b, one), 404, "not_found")
    refused(restore(b, two), 404, "not_found")


def test_a_write_from_another_site_or_not_json_is_refused_and_changes_nothing(pod_a: Pod):
    b, (one, two) = account_with(pod_a, 2)
    ok(delete(b, two))
    before = games(b)
    cookie = b.session()
    assert cookie is not None
    cases: list[tuple[str, Browser, dict[str, str]]] = [
        ("cross origin", Browser(pod_a, cookie=cookie, origin="https://evil.example"), {}),
        ("no origin, cross-site", Browser(pod_a, cookie=cookie, origin=None), {"Sec-Fetch-Site": "cross-site"}),
        ("no origin, none given", Browser(pod_a, cookie=cookie, origin=None), {}),
    ]
    for _label, other, headers in cases:
        for r in (other.http.post(f"/api/saves/{one}/delete", headers=headers),
                  other.http.post(f"/api/saves/{two}/restore", headers=headers),
                  other.http.post("/api/saves", headers=headers)):
            refused(r, 403, "cross_site")
    assert games(b) == before
    for path in (f"/api/saves/{one}/delete", f"/api/saves/{two}/restore", "/api/saves"):
        r = b.http.post(path, content=b"not json", headers={"Content-Type": "text/plain"})
        refused(r, 415, "not_json")
    assert games(b) == before
    same = Browser(pod_a, cookie=cookie, origin=None)
    ok(same.http.post(f"/api/saves/{two}/restore", headers={"Sec-Fetch-Site": "same-origin"}))
    ok(Browser(pod_a, cookie=cookie, origin=None).http.post(f"/api/saves/{two}/delete", headers={"Sec-Fetch-Site": "none"}))


@pytest.fixture
def owner_with_two(pod_a: Pod) -> tuple[Browser, list[Any]]:
    return account_with(pod_a, 2)


@pytest.fixture
def stranger_with_one(pod_a: Pod) -> tuple[Browser, Any]:
    """Another browser's account, holding one save."""
    b = Browser(pod_a)
    return b, begun(b)[0]


def test_another_account_cannot_see_delete_or_restore_a_save(owner_with_two: tuple[Browser, list[Any]],
                                                             stranger_with_one: tuple[Browser, Any]):
    a, (one, two) = owner_with_two
    b, own = stranger_with_one
    ok(delete(a, two))
    before_a = games(a)
    g = games(b)
    assert ids(g["saves"]) == [own] and g["deleted"] == []
    assert g["saves"][0]["number"] == 1
    refused(delete(b, one), 404, "not_found")
    refused(restore(b, two), 404, "not_found")
    refused(b.open(one), 404, "not_found")
    assert games(a) == before_a
    assert ids(games(b)["saves"]) == [own]


def test_a_join_brings_every_save_live_and_deleted(pod_a: Pod):
    t, (one, two, three) = account_with(pod_a, 3)
    ok(delete(t, two))
    code = ok(t.http.post("/api/me/transfer-code"))["transfer_code"]
    d = Browser(pod_a)
    mine, _ = begun(d)   # an account with no decision on any save
    j = ok(d.http.post("/api/join", json={"typed": code, "merge": False}))
    assert j["moved"] == 0
    after = games(d)
    assert after == games(t)
    assert sorted(ids(after["saves"])) == sorted([one, three])
    assert [x["save"]["save_id"] for x in after["deleted"]] == [two]
    refused(d.open(mine), 404, "not_found")
    ok(restore(d, two))
    assert sorted(ids(games(t)["saves"])) == sorted([one, two, three])


def test_a_join_from_a_browser_with_no_session_brings_every_save(pod_a: Pod):
    t, (one, two) = account_with(pod_a, 2)
    ok(delete(t, one))
    code = ok(t.http.post("/api/me/transfer-code"))["transfer_code"]
    d = Browser(pod_a)
    ok(d.http.post("/api/join", json={"typed": code, "merge": False}))
    assert games(d) == games(t)
    assert ids(games(d)["saves"]) == [two] and [x["save"]["save_id"] for x in games(d)["deleted"]] == [one]
