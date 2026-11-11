"""New accounts are limited: at most 10 an hour from one client address and 200 an hour in all, counted across pods; a
limit that cannot be counted refuses; only a POST /api/saves that would make an account is counted (CONTRACT.txt,
429 rate_limited). The client address is sent both as the connection's peer and as X-Forwarded-For (site.py).

The global count and the window are reached through the counter's rows (db/tables.py `tries`: one row per counted
request) rather than 200 requests, which would not fit the per-test time ceiling."""
import os

import psycopg

from tests.api_contract import rows
from tests.api_contract.site import Browser, Pod, fresh_address, ok, refused


def no_account_made(r_cookie: list[str]) -> None:
    assert not r_cookie, f"a refused Begin set a cookie: {r_cookie}"


def test_ten_new_accounts_an_hour_from_one_address_counted_across_pods(pg_url: str, pod_a: Pod, pod_b: Pod):
    here = fresh_address()
    made = [Browser(pod_a if i % 2 else pod_b, here) for i in range(10)]
    for b in made:
        ok(b.begin())
    r = Browser(pod_a, here).begin()
    refused(r, 429, "rate_limited")
    no_account_made(r.headers.get_list("set-cookie"))
    refused(Browser(pod_b, here).begin(), 429, "rate_limited")
    assert rows.count(pg_url, "accounts") == 10
    ok(made[0].begin())   # start over: no account made, so not counted
    ok(Browser(pod_b).begin())   # another address
    assert rows.count(pg_url, "accounts") == 11


def plant_tries(url: str, n: int, minutes_ago: int, same_who: bool) -> None:
    """n more counted account creations, `minutes_ago`, copied from the newest counter row; each from an address of
    its own unless `same_who`."""
    with psycopg.connect(url) as c:
        found = c.execute("SELECT kind, who FROM tries ORDER BY at DESC LIMIT 1").fetchone()
        assert found is not None, "an account creation left no counter row"
        kind, who = found
        for _ in range(n):
            c.execute("INSERT INTO tries (kind, who, at) VALUES (%s, %s, now() - make_interval(mins => %s))",
                      (kind, who if same_who else os.urandom(len(who)), minutes_ago))


def test_two_hundred_new_accounts_an_hour_in_all(pg_url: str, pod_a: Pod, pod_b: Pod):
    ok(Browser(pod_a).begin())
    assert rows.count(pg_url, "tries") == 1, "one account creation is not one counter row"
    plant_tries(pg_url, 198, 1, same_who=False)
    ok(Browser(pod_b).begin())   # the 200th
    r = Browser(pod_a).begin()
    refused(r, 429, "rate_limited")
    no_account_made(r.headers.get_list("set-cookie"))
    assert rows.count(pg_url, "accounts") == 2


def test_creations_over_an_hour_ago_no_longer_count(pg_url: str, pod_a: Pod):
    here = fresh_address()
    ok(Browser(pod_a, here).begin())
    rows.run(pg_url, "UPDATE tries SET at = now() - interval '61 minutes'")
    plant_tries(pg_url, 9, 61, same_who=True)   # ten from here, all over an hour ago
    ok(Browser(pod_a, here).begin())
    plant_tries(pg_url, 8, 0, same_who=True)   # nine from here this hour
    ok(Browser(pod_a, here).begin())   # the tenth
    refused(Browser(pod_a, here).begin(), 429, "rate_limited")


def test_a_limit_that_cannot_be_counted_refuses(pg_url: str, pod_a: Pod):
    player = Browser(pod_a)
    ok(player.begin())
    rows.run(pg_url, "ALTER TABLE tries RENAME TO tries_gone")
    r = Browser(pod_a).begin()
    refused(r, 429, "rate_limited")
    no_account_made(r.headers.get_list("set-cookie"))
    assert rows.count(pg_url, "accounts") == 1
    refused(player.begin(), 429, "rate_limited")   # a new game on an account is counted too (Games on one account)
    assert rows.count(pg_url, "saves") == 1
