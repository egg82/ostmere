"""An IPv6 client is counted by its /64, so one holder of a /48 (65,536 of them) would reach the site-wide caps alone and
lock everyone out. The limits therefore also count each /48, with an allowance of its own that is below the site-wide
cap: a prefix holder meets its own limit first. One /64 is still one client, and IPv4 is counted as before."""
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine

from ashfall_app.accounts import limits
from ashfall_app.db.engine import open_database
from tests.fake_clock import FakeClock

KEY = b"k" * 32
SUBNETS = 260   # more /64s than the site-wide new-account cap, in one /48


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url, max_size=4)
    yield database.engine
    database.close()


def in_prefix(prefix: int, subnet: int) -> str:
    return f"2001:db8:{prefix:x}:{subnet:x}::1"


def test_one_48_meets_its_own_account_limit_before_the_site_wide_one(engine: Engine):
    clock = FakeClock()
    got = [limits.refused(engine, KEY, in_prefix(1, n), clock()) for n in range(SUBNETS)]
    assert "overall" not in got
    assert got.count(None) == limits.PER_PREFIX and set(got[limits.PER_PREFIX:]) == {"prefix"}
    assert limits.refused(engine, KEY, in_prefix(2, 0), clock()) is None, "another /48 is not locked out"


def test_one_48_meets_its_own_join_limit_before_the_failed_join_cap(engine: Engine):
    clock = FakeClock()
    got = [limits.join_try(engine, KEY, in_prefix(1, n), clock()) for n in range(SUBNETS)]
    assert sum(r is None for r in got) < SUBNETS // 4, "most /64s of one /48 were let through"
    assert sum(r is None for r in got) == limits.JOIN_PER_PREFIX
    assert all(r.scope == "prefix" for r in got[limits.JOIN_PER_PREFIX:] if r is not None)
    assert limits.join_try(engine, KEY, in_prefix(2, 0), clock()) is None, "another /48 is not locked out"


def test_the_prefix_allowance_stays_below_the_site_wide_caps():
    assert limits.PER_ADDRESS < limits.PER_PREFIX < limits.OVERALL
    window_ratio = limits.JOIN_FAIL_WINDOW / limits.JOIN_WINDOW
    assert limits.JOIN_PER_ADDRESS < limits.JOIN_PER_PREFIX
    assert limits.JOIN_PER_PREFIX * window_ratio < limits.JOIN_FAILS, "a /48's failures alone cannot reach the cap"


def test_the_failed_join_cap_still_refuses_everyone(engine: Engine):
    clock = FakeClock()
    for _ in range(limits.JOIN_FAILS):
        limits.found_nothing(engine, clock())
    refusal = limits.join_try(engine, KEY, in_prefix(3, 0), clock())
    assert refusal is not None and refusal.scope == "overall"


def test_ipv4_addresses_in_one_block_are_counted_one_by_one(engine: Engine):
    clock = FakeClock()
    got = [limits.refused(engine, KEY, f"198.51.100.{n}", clock()) for n in range(1, 101)]
    assert got == [None] * 100
