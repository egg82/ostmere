"""Moving to another device, through the app on a database of the test's own (devices.py): codes and words made and
redeemed, each case of a join, what a join leaves in the database, and what it keeps out of it."""
import re
from collections.abc import Iterator
from datetime import timedelta

import pytest

import segno

from ashfall_app.accounts import limits, sessions
from ashfall_app.api import qr
from ashfall_app.main import join_key
from tests.accounts.devices import JOIN_KEY, Browser, Site, code_of, site


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def test_a_code_joins_a_browser_with_none_once(s: Site):
    a, b = Browser(s), Browser(s)
    save_id = a.play()
    r = a.code()
    body = r.json()
    code = code_of(r)
    assert re.fullmatch(r"[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}", code) and body["expires_in_s"] == 600
    assert body["join_url"] == "https://ostmere.yggdrasil.pub/#join=" + code
    assert r.headers["cache-control"] == "no-store"
    joined = b.join(code.lower().replace("-", " "))
    assert joined.status_code == 200, joined.text
    assert joined.json()["moved"] == 0 and b.session() and b.session() != a.session()
    assert [x["save_id"] for x in b.me()["saves"]] == [save_id]
    again = Browser(s).join(code)
    assert again.status_code == 404 and again.json()["code"] == "no_such_code"


def test_the_qr_is_the_link_drawn_by_segno(s: Site):
    a = Browser(s)
    a.begin()
    found = a.code().json()
    rows = found["qr"]
    side = len(rows)
    assert (side - 21) % 4 == 0 and all(len(r) == side and set(r) <= {"0", "1"} for r in rows)
    expected = segno.make(found["join_url"], error="m", micro=False)
    assert rows == ["".join("1" if m else "0" for m in row) for row in expected.matrix_iter(scale=1, border=0)]
    assert rows == qr.rows(found["join_url"])


def test_a_code_works_until_ten_minutes_and_not_after(s: Site):
    a = Browser(s)
    a.begin()
    first = code_of(a.code())
    s.clock.tick(minutes=9, seconds=59)
    assert Browser(s).join(first).status_code == 200
    second = code_of(a.code())
    s.clock.tick(minutes=10, seconds=1)
    assert Browser(s).join(second).status_code == 404


def test_a_new_code_ends_the_last_and_each_mint_sweeps_expired_ones(s: Site):
    a = Browser(s)
    a.begin()
    first = code_of(a.code())
    second = code_of(a.code())
    assert Browser(s).join(first).status_code == 404 and s.scalar("SELECT count(*) FROM transfer_codes") == 1
    account = s.scalar("SELECT id FROM accounts")
    s.run("INSERT INTO transfer_codes (account_id, code_hash, created_at, expires_at) SELECT :a, decode(md5(g::text),"
          " 'hex'), now() - interval '1 day', :exp FROM generate_series(1, 60) g", a=account,
          exp=s.clock() - timedelta(minutes=1))
    s.run("INSERT INTO transfer_codes (account_id, code_hash, created_at, expires_at) VALUES (:a, 'live', :t, :e)",
          a=account, t=s.clock(), e=s.clock() + timedelta(hours=1))
    b = Browser(s)
    b.begin()
    code_of(b.code())
    assert s.scalar("SELECT count(*) FROM transfer_codes WHERE expires_at <= :t", t=s.clock()) == 10   # 60 - 50
    assert s.scalar("SELECT count(*) FROM transfer_codes WHERE code_hash = 'live'") == 1   # a live one stays
    assert Browser(s).join(second).status_code == 200


def test_words_work_in_any_case_again_and_again_until_replaced(s: Site):
    a = Browser(s)
    a.play()
    r = a.words()
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store"
    said = r.json()["words"]
    assert r.json()["label"] == "Ostmere" and said.count("-") == 3
    assert a.me()["account"]["has_words"] is True and said not in str(a.me())
    assert Browser(s).join(said.upper().replace("-", ". ")).status_code == 200
    assert Browser(s).join(said).status_code == 200
    newer = a.words().json()["words"]
    assert Browser(s).join(said).status_code == 404
    assert Browser(s).join(newer).status_code == 200


def test_a_device_with_no_progress_moves_its_sessions_and_is_gone(s: Site):
    a, b = Browser(s), Browser(s)
    a.play()
    b.begin()   # a save with no decision
    b_account = s.scalar("SELECT account_id FROM sessions ORDER BY id DESC LIMIT 1")
    token = b.session()
    r = b.join(code_of(a.code()))
    assert r.status_code == 200 and b.session() == token   # the cookie stays; it names the other account now
    assert s.scalar("SELECT count(*) FROM accounts WHERE id = :b", b=b_account) == 0
    assert s.scalar("SELECT count(*) FROM saves WHERE account_id = :b", b=b_account) == 0
    assert s.scalar("SELECT count(*) FROM saves") == 1 and len(b.me()["saves"]) == 1


def test_a_device_with_progress_is_asked_and_nothing_changes(s: Site):
    a, b = Browser(s), Browser(s)
    a.play()
    s.clock.tick(hours=1)
    b.play()
    code = code_of(a.code())
    r = b.join(code)
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "confirm_merge" and body["step"] is None
    assert body["merge"] == {"here": 1, "there": 1, "there_newest_game_time": 0, "max_saves": 5,
                            "words_replaced": False}
    assert s.scalar("SELECT count(*) FROM accounts") == 2 and s.scalar("SELECT count(*) FROM transfer_codes") == 1
    assert Browser(s).join(code).status_code == 200   # not used up


def test_the_same_account_uses_a_code_but_not_words(s: Site):
    a = Browser(s)
    a.play()
    said = a.words().json()["words"]
    code = code_of(a.code())
    assert a.join(code).json()["moved"] == 0 and Browser(s).join(code).status_code == 404
    assert a.join(said).status_code == 200 and Browser(s).join(said).status_code == 200


def test_the_named_account_keeps_its_newest_sessions(s: Site, monkeypatch: pytest.MonkeyPatch):
    assert sessions.PER_ACCOUNT == 20   # control: the real number, cut here to keep the test fast
    monkeypatch.setattr(sessions, "PER_ACCOUNT", 3)
    a = Browser(s)
    a.play()
    for _ in range(3):
        s.clock.tick(1)
        assert Browser(s).join(code_of(a.code())).status_code == 200
    assert s.scalar("SELECT count(*) FROM sessions") == 3
    assert a.code().status_code == 401   # the one unused longest went


def test_words_come_due_after_three_days_of_progress(s: Site):
    a = Browser(s)
    a.begin()
    s.clock.tick(days=3)
    assert a.me()["account"]["words_due"] is False   # no progress
    b = Browser(s)
    b.play()
    assert b.me()["account"]["words_due"] is False
    s.clock.tick(days=3)
    assert b.me()["account"]["words_due"] is True
    b.words()
    assert b.me()["account"] == {"presentation": {"rules_opened": False, "devices_opened": False,
                                                  "reminder_mentioned": False, "ledger_lines": [], "mix_stopped": [], "switch_offered": [],
                                                  "journal_read": []},
                                 "settings": {"lessons": True}, "has_words": True, "words_due": False}


def test_not_a_code_and_a_wrong_code_both_find_nothing_but_only_the_wrong_one_counts(s: Site):
    for typed in ("hello", "AAAA-AAAA", "abandon ability able about"):
        r = Browser(s).join(typed)
        assert r.status_code == 404 and r.json()["code"] == "no_such_code" and typed not in r.text
    assert s.scalar("SELECT count(*) FROM tries WHERE kind = 'join_fail'") == 2


def test_ten_joins_per_quarter_hour_from_an_address_even_right_ones(s: Site):
    a = Browser(s)
    a.begin()
    b = Browser(s, "198.51.100.9")
    for _ in range(10):
        assert b.join("AAAA-AAAA").status_code == 404
    right = code_of(a.code())
    r = b.join(right)
    assert r.status_code == 429 and r.json()["code"] == "rate_limited" and int(r.headers["retry-after"]) == 900
    assert Browser(s, "198.51.100.10").join(right).status_code == 200   # another address


def test_three_hundred_misses_an_hour_close_joins_for_everyone(s: Site, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(limits, "JOIN_FAILS", 3)
    a = Browser(s)
    a.begin()
    for i in range(3):
        assert Browser(s, f"203.0.113.{i + 1}").join("AAAA-AAAA").status_code == 404
    assert Browser(s, "203.0.113.50").join(code_of(a.code())).status_code == 429
    s.clock.tick(hours=1, seconds=1)
    assert Browser(s, "203.0.113.51").join(code_of(a.code())).status_code == 200


def test_making_codes_and_words_is_capped_per_account(s: Site, monkeypatch: pytest.MonkeyPatch):
    assert (limits.CODES, limits.WORDS) == (10, 5)   # control: the real caps, cut here to keep the test fast
    monkeypatch.setattr(limits, "CODES", 3)
    monkeypatch.setattr(limits, "WORDS", 2)
    a = Browser(s)
    a.begin()
    assert [a.code().status_code for _ in range(4)] == [200] * 3 + [429]
    assert [a.words().status_code for _ in range(3)] == [200] * 2 + [429]
    r = a.words()
    assert 0 < int(r.headers["retry-after"]) <= 86400 and r.headers["cache-control"] == "no-store"


def test_the_per_kind_trim_keeps_other_kinds(s: Site):
    s.run("INSERT INTO tries (kind, who, at) VALUES ('words_make', 'x', :t), ('join', 'y', :old)",
          t=s.clock() - timedelta(hours=23), old=s.clock() - timedelta(minutes=16))
    Browser(s).join("AAAA-AAAA")
    assert s.scalar("SELECT count(*) FROM tries WHERE kind = 'words_make'") == 1
    assert s.scalar("SELECT count(*) FROM tries WHERE kind = 'join' AND who = 'y'") == 0   # past its own window


def test_no_account_and_the_routes_say_so(s: Site):
    b = Browser(s)
    for r in (b.code(), b.words()):
        assert r.status_code == 401 and r.json()["code"] == "no_account" and r.headers["cache-control"] == "no-store"


def test_the_join_key_is_sixty_four_hex_characters_or_none():
    assert join_key({"ASHFALL_JOIN_KEY": JOIN_KEY.hex()}) == JOIN_KEY
    assert join_key({"ASHFALL_JOIN_KEY": " " + JOIN_KEY.hex().upper() + "\n"}) == JOIN_KEY
    for bad in ({}, {"ASHFALL_JOIN_KEY": ""}, {"ASHFALL_JOIN_KEY": "zz" * 32}, {"ASHFALL_JOIN_KEY": JOIN_KEY.hex()[:62]},
                {"ASHFALL_JOIN_KEY": JOIN_KEY.hex() + "00"}):
        assert join_key(bad) is None, bad


@pytest.mark.parametrize("key", [None, "zz" * 32])   # one site each: building the app compiles every chapter
def test_without_the_join_key_nothing_is_made_or_joined(pg_url: str, monkeypatch: pytest.MonkeyPatch, key: str | None):
    with site(pg_url, monkeypatch, key) as s:
        a = Browser(s)
        a.begin()
        for r in (a.code(), a.words(), Browser(s).join("AAAA-AAAA")):
            assert r.status_code == 503 and r.json()["code"] == "save_unavailable", key


def test_no_code_or_words_rest_in_the_database_in_the_clear(s: Site):
    a = Browser(s)
    a.play()
    code = code_of(a.code())
    said = a.words().json()["words"]
    plain = code.replace("-", "")
    with s.db.connect() as c:
        dump = "\n".join(str(row) for t in ("accounts", "sessions", "transfer_codes", "tries")
                         for row in c.exec_driver_sql(f"SELECT * FROM {t}"))
        hexed = "\n".join(str(v) for (v,) in c.exec_driver_sql(
            "SELECT encode(code_hash, 'hex') FROM transfer_codes UNION ALL SELECT encode(words_hash, 'hex') FROM"
            " accounts UNION ALL SELECT encode(who, 'hex') FROM tries"))
    assert "h1$" in dump and "s1$" in dump, "the scan did not see the hashes"
    for secret in (code, plain, said, said.replace("-", " ")):
        for form in (secret, secret.lower(), secret.encode().hex()):
            assert form not in dump and form not in hexed, f"found {form!r}"
