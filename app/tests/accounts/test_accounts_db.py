"""Sessions, the account limit and the Postgres accounts service, against a database of the test's own."""
import hashlib
import hmac
import threading
from collections.abc import Iterator
from datetime import timedelta

import pytest
from sqlalchemy import Engine, select, text

from ashfall_app import logs
from ashfall_app.accounts import limits, sessions
from ashfall_app.accounts.interface import Limited
from ashfall_app.accounts.service import PgAccounts
from ashfall_app.db import accounts as rows
from ashfall_app.db import tries as tries_db
from ashfall_app.db.engine import open_database
from ashfall_app.db.tables import saves, sessions as sessions_table, tries
from ashfall_app.saves.interface import MAX_SAVES
from tests.fake_clock import FakeClock

KEY = b"k" * 32


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url, max_size=8)
    yield database.engine
    database.close()


def count(engine: Engine, table: str, where: str = "true") -> int:
    with engine.connect() as c:
        return int(c.execute(text(f"SELECT count(*) FROM {table} WHERE {where}")).scalar_one())


def test_a_session_is_stored_only_as_its_hash_and_found_by_its_token(engine: Engine):
    clock = FakeClock()
    with engine.begin() as c:
        acc = rows.create_account(c, clock())
        token = sessions.issue(c, acc, clock())
    with engine.connect() as c:
        stored = c.execute(select(sessions_table.c.token_hash)).scalar_one()
        assert stored == sessions.token_hash(token) and token.encode() not in stored
        found = sessions.current(c, token, clock())
        assert found is not None and found.account_id == acc
        assert sessions.current(c, token + "x", clock()) is None and sessions.current(c, None, clock()) is None
        assert sessions.current(c, token, clock() + timedelta(days=399)) is not None
        assert sessions.current(c, token, clock() + sessions.LIFETIME) is not None   # used exactly LIFETIME ago: alive
        assert sessions.current(c, token, clock.tick(days=400, seconds=1)) is None


def test_a_session_renews_at_most_daily(engine: Engine):
    clock = FakeClock()
    with engine.begin() as c:
        token = sessions.issue(c, rows.create_account(c, clock()), clock())
    for seconds, renewed in ((3600, False), (82799, False), (1, True), (60, False)):   # renewed a day after its last use
        clock.tick(seconds)
        with engine.begin() as c:
            found = sessions.current(c, token, clock())
            assert found is not None and sessions.renew(c, found, clock()) is renewed, seconds


def test_an_account_keeps_its_twenty_most_recently_used_sessions(engine: Engine):
    clock = FakeClock()
    with engine.begin() as c:
        acc = rows.create_account(c, clock())
        tokens = [sessions.issue(c, acc, clock.tick(1)) for _ in range(21)]
        assert sessions.current(c, tokens[0], clock()) is None
        assert all(sessions.current(c, t, clock()) is not None for t in tokens[1:])


def test_issuing_drops_sessions_unused_for_their_lifetime(engine: Engine):
    clock = FakeClock()
    with engine.begin() as c:
        sessions.issue(c, rows.create_account(c, clock()), clock())
        sessions.issue(c, rows.create_account(c, clock()), clock.tick(days=401))
    assert count(engine, "sessions") == 1


def test_ten_accounts_an_hour_from_one_address(engine: Engine):
    clock = FakeClock()
    assert [limits.refused(engine, KEY, "10.0.0.1", clock.tick(1)) for _ in range(11)] == [None] * 10 + ["address"]
    assert limits.refused(engine, KEY, "10.0.0.2", clock()) is None   # another address
    clock.tick(minutes=59, seconds=51)   # an hour and a second after the first try
    assert limits.refused(engine, KEY, "10.0.0.1", clock()) is None   # the first try left the window
    assert count(engine, "tries") == 11   # refusals are not counted


def test_the_account_limit_leaves_other_kinds_tries_alone(engine: Engine):
    clock = FakeClock()
    with engine.begin() as c:
        tries_db.add(c, "words_make", b"x", clock() - timedelta(hours=24))
    assert limits.refused(engine, KEY, "10.0.0.1", clock()) is None
    assert count(engine, "tries", "kind = 'words_make'") == 1


def test_two_hundred_an_hour_in_all(engine: Engine, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(limits, "OVERALL", 3)
    clock = FakeClock()
    assert [limits.refused(engine, KEY, f"10.0.0.{i}", clock()) for i in range(4)] == [None, None, None, "overall"]
    assert limits.OVERALL == 3 and limits.PER_ADDRESS == 10   # control: the real per-address limit still stands


def test_the_limit_holds_across_concurrent_requests(engine: Engine):
    """Twenty requests at once from one address, as two pods would send them: exactly ten get through."""
    clock = FakeClock()
    results: list[str | None] = []
    threads = [threading.Thread(target=lambda: results.append(limits.refused(engine, KEY, "10.9.9.9", clock())))
               for _ in range(20)]
    for th in threads:
        th.start()
    for th in threads:
        th.join(10)
    assert sorted(results, key=str) == [None] * 10 + ["address"] * 10
    assert count(engine, "tries") == 10


def test_an_address_is_stored_only_as_its_keyed_hash(engine: Engine):
    limits.refused(engine, KEY, "192.0.2.77", FakeClock()())
    with engine.connect() as c:
        who = c.execute(select(tries.c.who)).scalar_one()
    assert who == limits.client_key(KEY, "192.0.2.77") and b"192.0.2.77" not in who
    assert who != limits.client_key(b"other key" * 4, "192.0.2.77")


def test_a_client_is_keyed_by_its_ipv6_64_and_an_ipv4_mapped_address_as_ipv4():
    k = limits.client_key
    assert k(KEY, "2001:db8:1:2::1") == k(KEY, "2001:db8:1:2:ffff:ffff:ffff:ffff")   # one /64
    assert k(KEY, "2001:db8:1:2::1") != k(KEY, "2001:db8:1:3::1")   # another /64
    assert k(KEY, "::ffff:192.0.2.77") == k(KEY, "192.0.2.77")
    assert k(KEY, "192.0.2.77") != k(KEY, "192.0.2.78")
    assert k(KEY, "192.0.2.77") == hmac.new(KEY, b"192.0.2.77", hashlib.sha256).digest()   # IPv4 as before


def test_ten_accounts_an_hour_from_one_ipv6_64(engine: Engine):
    clock = FakeClock()
    got = [limits.refused(engine, KEY, f"2001:db8:1:2::{i:x}", clock()) for i in range(1, 12)]
    assert got == [None] * 10 + ["address"]


def test_the_limit_fails_closed(engine: Engine, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    clock = FakeClock()
    assert limits.refused(engine, None, "10.0.0.1", clock()) == "no_key"
    assert limits.refused(engine, b"", "10.0.0.1", clock()) == "no_key"
    with engine.begin() as c:
        c.execute(text("ALTER TABLE tries RENAME TO tries_gone"))
    assert limits.refused(engine, KEY, "10.0.0.1", clock()) == "error"
    out = capsys.readouterr().out
    assert "event=account.limited scope=no_key" in out and "event=account.limited scope=error" in out
    assert "event=account.limit_error" in out and "10.0.0.1" not in out


def test_the_service_makes_an_account_its_token_finds(engine: Engine, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    clock = FakeClock()
    service = PgAccounts(engine, clock, KEY, max_saves=MAX_SAVES)
    made = service.create("10.0.0.1")
    seen = service.who(made.token)
    assert seen is not None and seen.account_id == made.account_id and not service.renew(seen)
    assert service.who(None) is None and service.who("") is None and service.who("nope") is None
    clock.tick(days=1)
    seen = service.who(made.token)   # looking renews nothing
    assert seen is not None and seen.account_id == made.account_id
    assert service.renew(seen)
    again = service.who(made.token)
    assert again is not None and not service.renew(again)
    out = capsys.readouterr().out
    assert f"event=account.created account={made.account_id}" in out and "event=session.renewed" in out
    assert made.token not in out and "10.0.0.1" not in out


def test_the_service_refuses_past_the_limit(engine: Engine):
    service = PgAccounts(engine, FakeClock(), KEY, max_saves=MAX_SAVES)
    for _ in range(10):
        service.create("10.0.0.1")
    with pytest.raises(Limited) as refused:
        service.create("10.0.0.1")
    assert refused.value.scope == "address" and count(engine, "accounts") == 10


def test_making_an_account_prunes_empty_ones_unused_for_thirty_days(engine: Engine):
    clock = FakeClock()
    service = PgAccounts(engine, clock, KEY, max_saves=MAX_SAVES)
    empty = service.create("10.0.0.1").account_id
    played = service.create("10.0.0.2").account_id
    with engine.begin() as c:
        c.execute(saves.insert().values(account_id=played, created_at=clock(), started_at=clock(), updated_at=clock(),
                                        state="{}", format=4, rules_digest="d", decisions=1, game_time=0))
    clock.tick(days=30)
    service.create("10.0.0.3")
    assert count(engine, "accounts", f"id = {empty}") == 1   # unused exactly 30 days: kept
    clock.tick(1)
    service.create("10.0.0.4")
    assert count(engine, "accounts", f"id = {empty}") == 0 and count(engine, "accounts", f"id = {played}") == 1


def test_presentation_round_trips(engine: Engine):
    service = PgAccounts(engine, FakeClock(), KEY, max_saves=MAX_SAVES)
    acc = service.create("10.0.0.1").account_id
    first = service.about(acc)
    assert first is not None and first.presentation == {}
    kept = service.keep_presentation(acc, {"rule_seen": True, "rules_opened": False}, 512)
    assert kept is not None and kept.before == {} and kept.after == {"rule_seen": True, "rules_opened": False}
    after = service.about(acc)
    assert after is not None and after.presentation == kept.after
    assert service.about(acc + 1) is None and service.keep_presentation(acc + 1, {}, 512) is None
