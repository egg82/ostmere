"""Games on one account (CONTRACT.txt, "Games on one account"), through HTTP on one or two pods: the list, a new game
beside the others, the cap and the new-game limit, deleting (never the last live save, never loadable after) and
restoring, and requests racing each other across pods."""
import threading
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import httpx
import pytest

from tests.api_contract import rows
from tests.api_contract.site import SET_NO_ORDERS, Browser, Pod, begun, ok, refused

MAX_SAVES, KEPT_DAYS, NEW_GAMES_A_DAY = 5, 30, 10


def games(b: Browser) -> dict[str, Any]:
    return ok(b.http.get("/api/saves"))


def delete(b: Browser, save_id: object) -> httpx.Response:
    return b.http.post(f"/api/saves/{save_id}/delete")


def restore(b: Browser, save_id: object) -> httpx.Response:
    return b.http.post(f"/api/saves/{save_id}/restore")


def live_ids(b: Browser) -> list[int]:
    return [s["save_id"] for s in games(b)["saves"]]


def when(stamp: str) -> datetime:
    found = datetime.fromisoformat(stamp)
    assert found.tzinfo is not None, f"{stamp} names no zone"
    return found


def race(calls: list[Callable[[], httpx.Response]]) -> list[httpx.Response]:
    start = threading.Barrier(len(calls))
    answers: dict[int, httpx.Response] = {}

    def go(i: int, call: Callable[[], httpx.Response]) -> None:
        start.wait()
        answers[i] = call()

    threads = [threading.Thread(target=go, args=(i, c)) for i, c in enumerate(calls)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10)
    assert len(answers) == len(calls), "a request never answered"
    return [answers[i] for i in range(len(calls))]


def test_a_new_game_keeps_the_one_in_progress_and_numbers_count_on(pod_a: Pod):
    b = Browser(pod_a)
    first, _ = begun(b)
    ok(b.decide(first, SET_NO_ORDERS, 0))
    second, _ = begun(b)
    listed = games(b)
    assert [s["save_id"] for s in listed["saves"]] == [second, first]
    assert [s["number"] for s in listed["saves"]] == [2, 1]
    assert listed["deleted"] == [] and listed["max_saves"] == MAX_SAVES and listed["kept_days"] == KEPT_DAYS
    old = next(s for s in listed["saves"] if s["save_id"] == first)
    assert old["decisions"] == 1, "the game in progress lost its decision"
    new = listed["saves"][0]
    assert new["camp_level"] == 0 and new["decisions"] == 0 and new["game_time"] == 0
    assert when(new["started_at"]) <= when(new["played_at"])
    assert [s["save_id"] for s in ok(b.me())["saves"]] == [second, first]


def test_the_list_needs_an_account(pod_a: Pod):
    refused(Browser(pod_a).http.get("/api/saves"), 401, "no_account")


@pytest.fixture
def browser_at_the_cap(pod_a: Pod) -> Browser:
    """A browser holding MAX_SAVES live saves, begun in setup."""
    b = Browser(pod_a)
    for _ in range(MAX_SAVES):
        begun(b)
    return b


def test_the_cap_refuses_a_new_game_and_makes_nothing(pg_url: str, browser_at_the_cap: Browser):
    b = browser_at_the_cap
    refused(b.begin(), 409, "too_many_saves")
    assert rows.count(pg_url, "saves") == MAX_SAVES
    assert len(live_ids(b)) == MAX_SAVES


def test_a_deleted_save_is_held_listed_and_no_longer_counts(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    kept, _ = begun(b)
    gone, _ = begun(b)
    after = ok(delete(b, gone))
    assert [s["save_id"] for s in after["saves"]] == [kept]
    [held] = after["deleted"]
    assert held["save"]["save_id"] == gone and held["save"]["number"] == 2
    assert when(held["purge_at"]) - when(held["deleted_at"]) == timedelta(days=KEPT_DAYS)
    assert [s["save_id"] for s in ok(b.me())["saves"]] == [kept]
    assert games(b) == after
    for _ in range(MAX_SAVES - 1):
        begun(b)
    assert len(live_ids(b)) == MAX_SAVES, "a held deleted save took a place under the cap"
    assert rows.count(pg_url, "saves") == MAX_SAVES + 1


def test_a_deleted_save_cannot_be_loaded_or_played(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    gone, _ = begun(b)
    ok(delete(b, gone))
    for r in (b.open(gone), b.advance(gone), b.decide(gone, SET_NO_ORDERS, 0),
              b.http.post(f"/api/saves/{gone}/forecast"), b.dry_run(gone, [SET_NO_ORDERS])):
        refused(r, 404, "not_found")
    refused(delete(b, gone), 404, "not_found")


@pytest.fixture
def browser_after_a_delete(pod_a: Pod) -> Browser:
    """A browser that began two games and deleted the second, in setup."""
    b = Browser(pod_a)
    begun(b)
    gone, _ = begun(b)
    ok(delete(b, gone))
    return b


def test_a_number_is_not_given_again_while_its_save_is_held(browser_after_a_delete: Browser):
    b = browser_after_a_delete
    third = ok(b.begin())["save"]
    assert third["number"] == 3


def test_the_only_live_save_cannot_be_deleted(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    only, _ = begun(b)
    before = rows.the_save_row(pg_url)
    refused(delete(b, only), 409, "last_save")
    assert rows.the_save_row(pg_url) == before
    ok(b.open(only))


def test_another_accounts_save_is_not_found_to_delete_or_restore(pod_a: Pod):
    owner, other = Browser(pod_a), Browser(pod_a)
    begun(owner)
    theirs, _ = begun(owner)
    begun(other)
    refused(delete(other, theirs), 404, "not_found")
    ok(delete(owner, theirs))
    refused(restore(other, theirs), 404, "not_found")
    refused(delete(other, 999_999), 404, "not_found")


def test_restore_brings_the_save_back_as_it_was(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    gone, _ = begun(b)
    ok(b.decide(gone, SET_NO_ORDERS, 0))
    ok(delete(b, gone))
    back = ok(restore(b, gone))
    assert back["deleted"] == [] and gone in [s["save_id"] for s in back["saves"]]
    opened = ok(b.open(gone))
    assert opened["save"]["decisions"] == 1 and opened["save"]["number"] == 2
    refused(restore(b, gone), 404, "not_found")   # live now, so not a held deleted save


def test_restore_is_refused_at_the_cap(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    gone, _ = begun(b)
    ok(delete(b, gone))
    while len(live_ids(b)) < MAX_SAVES:
        begun(b)
    refused(restore(b, gone), 409, "too_many_saves")
    assert [d["save"]["save_id"] for d in games(b)["deleted"]] == [gone]


def test_new_games_past_the_days_limit_are_refused_with_retry_after(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    keep, _ = begun(b)   # the account's first save: counted by the account limit, not this one
    for _ in range(NEW_GAMES_A_DAY):
        made, _ = begun(b)
        ok(delete(b, made))
    r = b.begin()
    refused(r, 429, "rate_limited")
    assert int(r.headers["retry-after"]) > 0
    assert live_ids(b) == [keep]
    assert rows.count(pg_url, "saves") == NEW_GAMES_A_DAY + 1


def test_the_new_game_limit_is_per_account(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    for _ in range(NEW_GAMES_A_DAY):
        made, _ = begun(b)
        ok(delete(b, made))
    refused(b.begin(), 429, "rate_limited")
    other = Browser(pod_a)
    begun(other)
    begun(other)   # its second save: one counted on its own account


def test_two_pods_racing_new_games_never_pass_the_cap(pg_url: str, pod_a: Pod, pod_b: Pod):
    first = Browser(pod_a)
    for _ in range(MAX_SAVES - 2):
        begun(first)
    pages = [first.page_on(p) for p in (pod_a, pod_b, pod_a, pod_b)]
    answers = race([p.begin for p in pages])
    assert sorted(r.status_code for r in answers) == [200, 200, 409, 409], [r.text[:200] for r in answers]
    assert len(live_ids(first)) == MAX_SAVES and rows.count(pg_url, "saves") == MAX_SAVES
    assert sorted(s["number"] for s in games(first)["saves"]) == list(range(1, MAX_SAVES + 1))


def test_two_pods_racing_deletes_keep_one_live_save(pod_a: Pod, pod_b: Pod):
    one = Browser(pod_a)
    a, _ = begun(one)
    b, _ = begun(one)
    two = one.page_on(pod_b)
    answers = race([lambda: delete(one, a), lambda: delete(two, b)])
    assert sorted(r.status_code for r in answers) == [200, 409], [r.text[:200] for r in answers]
    assert refused(next(r for r in answers if r.status_code == 409), 409, "last_save")
    assert len(live_ids(one)) == 1 and len(games(one)["deleted"]) == 1


def test_a_delete_racing_a_new_game_at_the_cap_leaves_a_consistent_count(pod_a: Pod, pod_b: Pod):
    one = Browser(pod_a)
    ids = [begun(one)[0] for _ in range(MAX_SAVES)]
    two = one.page_on(pod_b)
    deleted, made = race([lambda: delete(one, ids[0]), two.begin])
    ok(deleted)
    assert made.status_code in (200, 409), made.text[:200]
    assert len(live_ids(one)) == MAX_SAVES - (made.status_code == 409)


def test_a_delete_racing_play_on_that_save_leaves_it_unloadable(pod_a: Pod, pod_b: Pod):
    one = Browser(pod_a)
    begun(one)
    target, _ = begun(one)
    two = one.page_on(pod_b)
    gone, played = race([lambda: delete(one, target), lambda: two.decide(target, SET_NO_ORDERS, 0)])
    ok(gone)
    assert played.status_code in (200, 404), played.text[:200]
    refused(two.open(target), 404, "not_found")
    held = games(one)["deleted"][0]["save"]
    assert held["decisions"] == (1 if played.status_code == 200 else 0)
