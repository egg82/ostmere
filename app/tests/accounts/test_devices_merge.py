"""The merge (CONTRACT.txt, "Moving to another device", POST /api/join with merge): a browser whose account holds
games of its own moves them into the account a code or words name, through the app on a database of the test's own
(devices.py). Each refusal moves nothing; only the requesting session's own games ever move, and only one way."""
from collections.abc import Iterator
from typing import Any

import pytest

from ashfall_app import logs
from ashfall_app.db import joins
from tests.accounts.devices import JOIN_KEY, Browser, Site, code_of, site


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def games(b: Browser, n: int) -> list[int]:
    """n games begun and played once each on this browser's account, one second apart; their save ids."""
    played: list[int] = []
    for _ in range(n):
        played.append(b.play())
        b.site.clock.tick(1)
    return played


def owners(s: Site) -> dict[int, int]:
    """Every save's account, deleted saves included."""
    with s.db.connect() as c:
        return {int(i): int(a) for i, a in c.exec_driver_sql("SELECT id, account_id FROM saves")}


def numbers(s: Site, account_id: int) -> dict[int, int | None]:
    with s.db.connect() as c:
        return {int(i): n for i, n in c.exec_driver_sql(
            f"SELECT id, number FROM saves WHERE account_id = {int(account_id)}")}


def account_of(s: Site, save_id: int) -> int:
    found: int = s.scalar("SELECT account_id FROM saves WHERE id = :i", i=save_id)
    return found


def summary(r: Any) -> dict[str, Any]:
    found: dict[str, Any] = r.json()["merge"]
    return found


def test_a_merge_moves_every_game_of_this_device_numbered_after_the_named_accounts(s: Site):
    a, b = Browser(s), Browser(s)
    there = games(a, 2)
    here = games(b, 3)
    assert b.http.post(f"/api/saves/{here[1]}/delete").status_code == 200   # a deleted game moves too
    t, d = account_of(s, there[0]), account_of(s, here[0])
    token = b.session()
    r = b.join(code_of(a.code()), merge=True)
    assert r.status_code == 200, r.text
    assert r.json()["moved"] == 3 and b.session() == token   # the cookie stays; it names the other account now
    assert all(owners(s)[i] == t for i in there + here)
    assert numbers(s, t) == {there[0]: 1, there[1]: 2, here[0]: 3, here[1]: 4, here[2]: 5}   # in this device's order
    assert s.scalar("SELECT count(*) FROM accounts WHERE id = :d", d=d) == 0
    listed = b.http.get("/api/saves").json()
    assert sorted(x["save_id"] for x in listed["saves"]) == sorted(there + [here[0], here[2]])
    assert [x["save"]["save_id"] for x in listed["deleted"]] == [here[1]]
    assert sorted(x["save_id"] for x in a.me()["saves"]) == sorted(there + [here[0], here[2]])
    assert Browser(s).join(code_of(a.code())).status_code == 200   # the account still makes and takes codes


def test_a_merge_that_would_pass_the_cap_is_refused_and_nothing_moves(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 3)
    games(b, 3)
    before = owners(s)
    code = code_of(a.code())
    for merge in (True, False):   # refused before the question too, so the page never offers a move that cannot go
        r = b.join(code, merge)
        assert r.status_code == 409, r.text
        assert r.json()["code"] == "too_many_saves"
        assert summary(r) == {"here": 3, "there": 3, "there_newest_game_time": 0, "max_saves": 5,
                              "words_replaced": False}
    assert owners(s) == before and s.scalar("SELECT count(*) FROM accounts") == 2
    assert Browser(s).join(code).status_code == 200   # the code was not used up


def test_exactly_at_the_cap_moves(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 3)
    games(b, 2)
    r = b.join(code_of(a.code()), merge=True)
    assert r.status_code == 200 and r.json()["moved"] == 2 and len(b.me()["saves"]) == 5


@pytest.fixture
def two_accounts_of_one(s: Site) -> tuple[Browser, Browser]:
    """Two browsers, each on an account holding one played game, built in setup."""
    a, b = Browser(s), Browser(s)
    games(a, 1)
    games(b, 1)
    return a, b


def test_a_device_that_fits_is_asked_first_and_told_the_cap(s: Site, two_accounts_of_one: tuple[Browser, Browser]):
    a, b = two_accounts_of_one
    before = owners(s)
    r = b.join(code_of(a.code()))
    assert r.status_code == 409 and r.json()["code"] == "confirm_merge"
    assert summary(r) == {"here": 1, "there": 1, "there_newest_game_time": 0, "max_saves": 5,
                              "words_replaced": False}
    assert owners(s) == before


def test_a_wrong_or_expired_code_moves_nothing(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    games(b, 1)
    before = owners(s)
    code = code_of(a.code())
    s.clock.tick(minutes=10, seconds=1)
    for typed in (code, "AAAA-AAAA", "abandon ability able about"):
        r = b.join(typed, merge=True)
        assert r.status_code == 404 and r.json()["code"] == "no_such_code", typed
    assert owners(s) == before and s.scalar("SELECT count(*) FROM accounts") == 2


def test_only_the_requesting_sessions_own_games_move_and_only_into_the_named_account(s: Site):
    a, b, c = Browser(s), Browser(s), Browser(s)
    there, here, bystander = games(a, 1), games(b, 2), games(c, 2)
    t, other = account_of(s, there[0]), account_of(s, bystander[0])
    forged = Browser(s)
    forged.http.cookies.set("__Host-ashfall_session", "not-a-session", domain="testserver")
    r = forged.join(code_of(a.code()), merge=True)   # no live session: it joins and moves nothing
    assert r.status_code == 200 and r.json()["moved"] == 0
    assert b.join(code_of(a.code()), merge=True).json()["moved"] == 2
    found = owners(s)
    assert [found[i] for i in there + here] == [t] * 3
    assert [found[i] for i in bystander] == [other] * 2   # another account's games never move
    assert len(c.me()["saves"]) == 2


def test_the_named_account_never_moves_into_this_one(s: Site):
    a, b = Browser(s), Browser(s)
    there, here = games(a, 2), games(b, 1)
    t = account_of(s, there[0])
    said = a.words().json()["words"]
    assert b.join(said, merge=True).status_code == 200   # by words this time
    assert {owners(s)[i] for i in there + here} == {t} and s.scalar("SELECT count(*) FROM accounts") == 1


def test_a_code_for_the_same_account_moves_nothing_and_is_used_up(s: Site):
    a = Browser(s)
    mine = games(a, 2)
    before = owners(s)
    code = code_of(a.code())
    r = a.join(code, merge=True)
    assert r.status_code == 200 and r.json()["moved"] == 0
    assert owners(s) == before and numbers(s, before[mine[0]]) == {mine[0]: 1, mine[1]: 2}
    assert Browser(s).join(code).status_code == 404


def test_this_devices_words_become_the_named_accounts_when_it_has_none(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    games(b, 1)
    said = b.words().json()["words"]
    assert b.join(code_of(a.code()), merge=True).status_code == 200
    assert b.me()["account"]["has_words"] is True
    assert Browser(s).join(said).status_code == 200 and s.scalar("SELECT count(*) FROM accounts") == 1


def test_the_named_accounts_own_words_are_kept_over_this_devices(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    games(b, 1)
    theirs, mine = a.words().json()["words"], b.words().json()["words"]
    assert b.join(code_of(a.code()), merge=True).status_code == 200
    assert Browser(s).join(theirs).status_code == 200 and Browser(s).join(mine).status_code == 404


@pytest.fixture
def word_pairs(s: Site) -> list[tuple[Browser, Browser]]:
    """Two accounts of one game each for every combination of (this device, the other) having words, built in setup."""
    pairs: list[tuple[Browser, Browser]] = []
    for here_words, there_words in ((False, False), (True, False), (False, True), (True, True)):
        a, b = Browser(s), Browser(s)
        games(a, 1)
        games(b, 1)
        if there_words:
            a.words()
        if here_words:
            b.words()
        pairs.append((a, b))
    return pairs


def test_the_question_says_when_this_devices_words_will_stop_working(word_pairs: list[tuple[Browser, Browser]]):
    """words_replaced only when both accounts have words: then this device's words stop working, unannounced unless
    the page is told."""
    seen: list[bool] = []
    for a, b in word_pairs:
        r = b.join(code_of(a.code()))
        assert r.status_code == 409 and r.json()["code"] == "confirm_merge", r.text
        seen.append(summary(r)["words_replaced"])
    assert seen == [False, False, False, True]


def test_a_merge_that_fails_partway_moves_nothing(s: Site, monkeypatch: pytest.MonkeyPatch):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    games(b, 2)
    before = owners(s)
    code = code_of(a.code())

    def broken(*_: object) -> int:
        raise RuntimeError("planted: the fold fails after the saves moved")

    with monkeypatch.context() as m:
        m.setattr(joins, "delete_empty_account", broken)
        assert b.join(code, merge=True).status_code == 500
    assert owners(s) == before and s.scalar("SELECT count(*) FROM accounts") == 2
    assert b.join(code, merge=True).status_code == 200   # the failed try did not use the code up


def test_a_merge_is_logged_with_ids_and_counts_never_secrets(s: Site, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    capsys.readouterr()
    a, b = Browser(s, "203.0.113.61"), Browser(s, "203.0.113.62")
    there, here = games(a, 1), games(b, 2)
    t, d = account_of(s, there[0]), account_of(s, here[0])
    code = code_of(a.code())
    assert b.join(code, merge=True).status_code == 200
    out = capsys.readouterr().out
    line = next((x for x in out.splitlines() if "event=join.ok" in x), "")
    assert f"account={t}" in line and f"from={d}" in line and "moved=2" in line, line
    for secret in (code, code.replace("-", ""), a.session() or "?", b.session() or "?", "203.0.113.6", JOIN_KEY.hex()):
        assert secret not in out
