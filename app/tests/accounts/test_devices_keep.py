"""Joining without moving (CONTRACT.txt, "Moving to another device", POST /api/join with keep): a browser whose account
holds games signs into the named account and leaves its games on its old one, which stays in the database with its
recovery words, made by the join when it had none. Through the app on a database of the test's own (devices.py)."""
from collections.abc import Iterator

import pytest

from ashfall_app.accounts.service import EMPTY_KEPT
from tests.accounts.devices import Browser, Site, code_of, site
from tests.accounts.test_devices_merge import account_of, games, numbers, owners


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def test_a_join_that_keeps_leaves_every_game_where_it_was_and_signs_this_browser_into_the_other_account(s: Site):
    a, b = Browser(s), Browser(s)
    there, here = games(a, 2), games(b, 3)
    assert b.http.post(f"/api/saves/{here[1]}/delete").status_code == 200
    t, d = account_of(s, there[0]), account_of(s, here[0])
    owned, numbered = owners(s), {t: numbers(s, t), d: numbers(s, d)}
    token = b.session()
    r = b.join(code_of(a.code()), keep=True)
    assert r.status_code == 200, r.text
    assert r.json()["moved"] == 0 and b.session() == token
    assert owners(s) == owned and numbers(s, t) == numbered[t] and numbers(s, d) == numbered[d]
    assert s.scalar("SELECT count(*) FROM accounts WHERE id = :d", d=d) == 1
    assert sorted(x["save_id"] for x in b.me()["saves"]) == sorted(there)   # this browser is T's now


def test_the_games_left_behind_come_back_with_the_words_the_join_made(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    here = games(b, 2)
    r = b.join(code_of(a.code()), keep=True)
    kept = r.json()["kept"]
    assert kept["saves"] == 2 and kept["label"] == "Ostmere" and len(kept["words"].split("-")) == 4
    back = Browser(s)
    assert back.join(kept["words"]).status_code == 200
    assert sorted(x["save_id"] for x in back.me()["saves"]) == sorted(here)
    assert s.scalar("SELECT count(*) FROM accounts WHERE words_hash IS NOT NULL") == 1


def test_a_device_that_already_had_words_keeps_them_and_is_told_none_are_shown(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    here = games(b, 1)
    said = b.words().json()["words"]
    before = s.scalar("SELECT words_hash FROM accounts WHERE id = :d", d=account_of(s, here[0]))
    r = b.join(code_of(a.code()), keep=True)
    assert r.status_code == 200 and r.json()["kept"] == {"saves": 1, "words": None, "label": "Ostmere"}
    assert s.scalar("SELECT words_hash FROM accounts WHERE id = :d", d=account_of(s, here[0])) == before
    back = Browser(s)
    assert back.join(said).status_code == 200 and [x["save_id"] for x in back.me()["saves"]] == here


def test_only_the_asking_browser_leaves_its_old_account(s: Site):
    a, b, c = Browser(s), Browser(s), Browser(s)
    games(a, 1)
    here = games(b, 1)
    assert c.join(code_of(b.code())).status_code == 200   # c is a second browser of b's account
    assert b.join(code_of(a.code()), keep=True).status_code == 200
    assert [x["save_id"] for x in c.me()["saves"]] == here
    assert len(b.me()["saves"]) == 1 and b.me()["saves"][0]["save_id"] != here[0]


def test_games_kept_on_a_forgotten_account_survive_the_empty_account_prune(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    here = games(b, 2)
    d = account_of(s, here[0])
    assert b.join(code_of(a.code()), keep=True).status_code == 200
    s.clock.tick(days=EMPTY_KEPT.days + 5)
    Browser(s).begin()   # making an account prunes the empty ones unused for EMPTY_KEPT
    assert s.scalar("SELECT count(*) FROM accounts WHERE id = :d", d=d) == 1
    assert s.scalar("SELECT count(*) FROM saves WHERE account_id = :d", d=d) == 2


def test_a_keep_is_not_held_to_the_cap_because_nothing_moves(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 3)
    games(b, 3)
    assert b.join(code_of(a.code()), keep=True).status_code == 200


def test_a_device_without_games_just_folds_in_and_has_nothing_kept(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    b.begin()
    d = account_of(s, b.me()["saves"][0]["save_id"])
    r = b.join(code_of(a.code()), keep=True)
    assert r.status_code == 200 and r.json()["kept"] is None
    assert s.scalar("SELECT count(*) FROM accounts WHERE id = :d", d=d) == 0


def test_a_refused_keep_makes_no_words_and_uses_no_code(s: Site):
    a, b = Browser(s), Browser(s)
    games(a, 1)
    here = games(b, 1)
    assert b.join("AAAA-AAAA", keep=True).status_code == 404
    assert s.scalar("SELECT words_hash FROM accounts WHERE id = :d", d=account_of(s, here[0])) is None
    assert b.join(code_of(a.code()), merge=True, keep=True).status_code == 422
    assert s.scalar("SELECT words_hash FROM accounts WHERE id = :d", d=account_of(s, here[0])) is None
