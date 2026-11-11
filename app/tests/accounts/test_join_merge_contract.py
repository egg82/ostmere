"""The account merge on POST /api/join, written from api/CONTRACT.txt alone ("Moving to another device"; "Games on
one account"): what a join moves, what it refuses, who owns what afterwards, and the recovery words."""
from collections.abc import Iterator
from typing import Any

import pytest

from tests.accounts.devices import Browser, Site, code_of, site


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def games(b: Browser) -> dict[str, Any]:
    found: dict[str, Any] = b.http.get("/api/saves").json()
    return found


def live_ids(b: Browser) -> list[int]:
    return sorted(x["save_id"] for x in games(b)["saves"])


def deleted_ids(b: Browser) -> list[int]:
    return sorted(x["save"]["save_id"] for x in games(b)["deleted"])


def numbers(b: Browser) -> dict[int, int | None]:
    """Every save the account holds, live or deleted, by id to number."""
    g = games(b)
    infos: list[dict[str, Any]] = [*g["saves"], *(x["save"] for x in g["deleted"])]
    return {x["save_id"]: x["number"] for x in infos}


def delete(b: Browser, save_id: int) -> None:
    r = b.http.post(f"/api/saves/{save_id}/delete")
    assert r.status_code == 200, r.text


def with_games(b: Browser, live: int) -> list[int]:
    """A browser whose account holds `live` live saves, the first with a decision."""
    ids = [b.play()]
    ids += [b.begin()["save"]["save_id"] for _ in range(live - 1)]
    return ids


def error_code(r: Any) -> str:
    found: str = r.json()["code"]
    return found


def words_of(b: Browser) -> str:
    r = b.words()
    assert r.status_code == 200, r.text
    found: str = r.json()["words"]
    return found


def question(t: Browser, d: Browser) -> dict[str, Any]:
    """What d is asked when it joins t's account without merge."""
    r = d.join(code_of(t.code()))
    assert r.status_code == 409 and error_code(r) == "confirm_merge", r.text
    found: dict[str, Any] = r.json()["merge"]
    return found


def test_a_merge_moves_every_save_of_the_joiner_deleted_ones_included(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 1)
    d_ids = with_games(d, 3)
    delete(d, d_ids[2])
    r = d.join(code_of(t.code()), merge=True)
    assert r.status_code == 200, r.text
    assert r.json()["moved"] == 3
    assert live_ids(d) == sorted(t_ids + d_ids[:2])
    assert deleted_ids(d) == [d_ids[2]]
    assert live_ids(t) == live_ids(d) and deleted_ids(t) == [d_ids[2]]


def test_moved_saves_are_numbered_after_the_highest_the_named_account_holds_in_their_own_order(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 3)
    delete(t, t_ids[2])   # its number 3 still counts
    d_ids = with_games(d, 3)
    delete(d, d_ids[2])
    before = numbers(d)
    assert d.join(code_of(t.code()), merge=True).status_code == 200
    after = numbers(d)
    assert after[t_ids[0]] == 1 and after[t_ids[1]] == 2 and after[t_ids[2]] == 3
    order = sorted(d_ids, key=lambda i: before[i] or 0)
    assert [after[i] for i in order] == [4, 5, 6]
    assert sorted(n or 0 for n in after.values()) == [1, 2, 3, 4, 5, 6]


@pytest.fixture
def two_accounts_of_three(s: Site) -> tuple[Browser, Browser, list[int], list[int]]:
    """t and d, each holding three live saves, built in setup: the browsers, then their save ids."""
    t, d = Browser(s), Browser(s)
    return t, d, with_games(t, 3), with_games(d, 3)


def test_a_merge_over_the_cap_is_refused_merge_or_not_and_the_code_survives(
        two_accounts_of_three: tuple[Browser, Browser, list[int], list[int]]):
    t, d, t_ids, d_ids = two_accounts_of_three
    code = code_of(t.code())
    for merge in (False, True):
        r = d.join(code, merge=merge)
        assert r.status_code == 409 and error_code(r) == "too_many_saves", r.text
        summary = r.json()["merge"]
        assert (summary["here"], summary["there"], summary["max_saves"]) == (3, 3, 5)
        assert live_ids(d) == sorted(d_ids) and live_ids(t) == sorted(t_ids)
        assert d.me()["saves"] and d.join("not a code").status_code == 404
    delete(d, d_ids[2])
    r = d.join(code, merge=True)
    assert r.status_code == 200 and r.json()["moved"] == 3, r.text
    assert len(live_ids(d)) == 5


def test_a_merge_to_exactly_the_cap_goes_through_and_deleted_saves_do_not_count(s: Site):
    t, d = Browser(s), Browser(s)
    with_games(t, 3)
    d_ids = with_games(d, 3)
    delete(d, d_ids[2])
    delete(d, d_ids[1])
    extra = d.begin()["save"]["save_id"]
    delete(d, extra)
    r = d.join(code_of(t.code()), merge=True)
    assert r.status_code == 200, r.text
    assert len(live_ids(d)) == 4 and len(deleted_ids(d)) == 3


def test_an_unknown_or_expired_code_and_unknown_words_are_404_and_move_nothing(s: Site):
    t, d = Browser(s), Browser(s)
    with_games(t, 1)
    d_ids = with_games(d, 2)
    code = code_of(t.code())
    stale = code_of(t.code())   # ends the first
    s.clock.tick(minutes=10, seconds=1)
    for typed in ("ZZZZ-ZZZZ", code, stale, "alpha-beta-gamma-delta", ""):
        r = d.join(typed, merge=True)
        assert r.status_code == 404 and error_code(r) == "no_such_code", (typed, r.text)
    assert live_ids(d) == sorted(d_ids) and len(live_ids(t)) == 1


def test_replaced_words_find_nothing_and_a_code_is_not_used_up_by_a_refusal(s: Site):
    t, d = Browser(s), Browser(s)
    with_games(t, 1)
    old = words_of(t)
    words_of(t)
    d_ids = with_games(d, 1)
    assert d.join(old, merge=True).status_code == 404
    assert live_ids(d) == d_ids
    code = code_of(t.code())
    assert d.join(code).status_code == 409
    assert d.join(code, merge=True).status_code == 200


def test_a_code_naming_the_joiners_own_account_changes_nothing_and_is_used_up(s: Site):
    a = Browser(s)
    ids = with_games(a, 2)
    code = code_of(a.code())
    r = a.join(code, merge=True)
    assert r.status_code == 200 and r.json()["moved"] == 0, r.text
    assert live_ids(a) == sorted(ids) and deleted_ids(a) == []
    again = Browser(s).join(code)
    assert again.status_code == 404


@pytest.fixture
def three_accounts(s: Site) -> tuple[Browser, Browser, Browser, list[int], list[int], list[int]]:
    """Three accounts of two live saves each, built in setup: t, d and c, then their save ids in that order."""
    t, d, c = Browser(s), Browser(s), Browser(s)
    return t, d, c, with_games(t, 2), with_games(d, 2), with_games(c, 2)


def test_a_third_account_never_moves_and_the_named_games_stay_the_named_accounts(
        three_accounts: tuple[Browser, Browser, Browser, list[int], list[int], list[int]]):
    t, d, c, t_ids, d_ids, c_ids = three_accounts
    c_numbers = numbers(c)
    assert d.join(code_of(t.code()), merge=True).status_code == 200
    assert live_ids(c) == sorted(c_ids) and numbers(c) == c_numbers
    assert not set(live_ids(c)) & set(live_ids(d))
    assert live_ids(t) == sorted(t_ids + d_ids)
    assert live_ids(d) == sorted(t_ids + d_ids)


def test_the_named_accounts_games_keep_their_numbers_and_never_move_to_the_joiner(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 2)
    with_games(d, 1)
    t_before = numbers(t)
    assert d.join(code_of(t.code()), merge=True).status_code == 200
    assert {i: numbers(t)[i] for i in t_ids} == {i: t_before[i] for i in t_ids}
    assert t.session() != d.session()


def test_after_a_merge_the_joiners_session_sees_the_named_games_plus_its_own(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 2)
    d_ids = with_games(d, 2)
    r = d.join(code_of(t.code()), merge=True)
    assert r.status_code == 200
    me = d.me()
    assert sorted(x["save_id"] for x in me["saves"]) == sorted(t_ids + d_ids)
    save_id = d_ids[0]
    assert d.http.post(f"/api/saves/{save_id}/forecast", json={"decisions": []}).status_code == 200
    assert t.http.get("/api/saves").status_code == 200 and sorted(live_ids(t)) == sorted(t_ids + d_ids)


def test_a_join_from_a_device_with_games_without_merge_asks_first_and_moves_nothing(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 2)
    d_ids = with_games(d, 1)
    cookie = d.session()
    summary = question(t, d)
    assert (summary["here"], summary["there"], summary["max_saves"]) == (1, 2, 5)
    assert live_ids(d) == d_ids and live_ids(t) == sorted(t_ids) and d.session() == cookie


def test_the_question_carries_the_game_time_of_the_named_accounts_newest_save(s: Site):
    t, d = Browser(s), Browser(s)
    with_games(d, 1)
    t.begin()
    assert question(t, d)["there_newest_game_time"] is not None


@pytest.mark.parametrize(("t_words", "d_words", "replaced"),
                         [(True, True, True), (True, False, False), (False, True, False), (False, False, False)])
def test_words_replaced_is_true_only_when_both_accounts_have_words(s: Site, t_words: bool, d_words: bool,
                                                                    replaced: bool):
    t, d = Browser(s), Browser(s)
    with_games(t, 1)
    with_games(d, 1)
    if t_words:
        words_of(t)
    if d_words:
        words_of(d)
    assert question(t, d)["words_replaced"] is replaced


def test_after_a_merge_the_joiners_old_words_find_nothing_and_the_named_words_restore_every_game(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 1)
    d_ids = with_games(d, 2)
    t_words, d_words = words_of(t), words_of(d)
    assert d.join(code_of(t.code()), merge=True).status_code == 200
    gone = Browser(s).join(d_words)
    assert gone.status_code == 404 and error_code(gone) == "no_such_code"
    fresh = Browser(s)
    r = fresh.join(t_words)
    assert r.status_code == 200, r.text
    assert live_ids(fresh) == sorted(t_ids + d_ids)


def test_the_joiners_words_become_the_named_accounts_when_it_has_none(s: Site):
    t, d = Browser(s), Browser(s)
    t_ids = with_games(t, 1)
    d_ids = with_games(d, 1)
    d_words = words_of(d)
    assert d.join(code_of(t.code()), merge=True).status_code == 200
    fresh = Browser(s)
    assert fresh.join(d_words).status_code == 200
    assert live_ids(fresh) == sorted(t_ids + d_ids)
