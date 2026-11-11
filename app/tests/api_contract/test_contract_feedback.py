"""Tester feedback (api/CONTRACT.txt, "POST /api/feedback"): 1 to 2000 characters from any browser, kept with the build
and, when the browser's account owns the save, where in the game it was; limited per account (or per client address
without one) and in all; and the words never reach a log line. Rows are read where HTTP cannot reach."""
from collections.abc import Iterator
from typing import Any

import psycopg
import pytest

from tests.api_contract import rows
from tests.api_contract.site import Browser, Pod, begun, fresh_address, ok, pod, refused

WORDS = "the third tap felt wrong, uniquely: quokka-7731"


def stored(url: str) -> list[dict[str, Any]]:
    with psycopg.connect(url) as c:
        cur = c.execute("SELECT id, text, build, release, account_id, save_id, game_time, last_line, created_at "
                        "FROM feedback ORDER BY id")
        names = [d.name for d in cur.description or []]
        return [dict(zip(names, r)) for r in cur.fetchall()]


def sent(r: Any) -> None:
    assert r.status_code == 204, f"{r.status_code} {r.text[:200]}"
    assert r.content == b""


def test_a_browser_with_no_account_is_heard(pg_url: str, pod_a: Pod):
    sent(Browser(pod_a).feedback(WORDS))
    [row] = stored(pg_url)
    assert row["text"] == WORDS
    assert row["build"] == "contract-build-a" and isinstance(row["release"], int)
    assert (row["account_id"], row["save_id"], row["game_time"], row["last_line"]) == (None, None, None, None)


def test_an_account_with_its_own_save_is_kept_with_where_it_was(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    save_id, step = begun(b)
    sent(b.feedback(WORDS, save_id))
    with psycopg.connect(pg_url) as c:   # lines the game wrote since, which HTTP does not reach
        c.execute("INSERT INTO save_lines (save_id, n, at, key) VALUES (%s, 50, 5, 'l_older'), (%s, 51, 9, 'l_newest')",
                  (save_id, save_id))
    sent(b.feedback(WORDS, save_id))
    first, second = stored(pg_url)
    for row in (first, second):
        assert row["save_id"] == save_id and row["account_id"] == rows.scalar(pg_url, "SELECT id FROM accounts")
        assert row["game_time"] == step["view"]["at"]
    assert (first["last_line"], second["last_line"]) == (None, "l_newest")


def test_a_save_that_is_not_the_browsers_is_not_recorded(pg_url: str, pod_a: Pod):
    other_save, _ = begun(Browser(pod_a))
    mine = Browser(pod_a)
    begun(mine)
    sent(mine.feedback(WORDS, other_save))
    sent(Browser(pod_a).feedback(WORDS, other_save))   # no account at all
    sent(mine.feedback(WORDS, 987654321))   # no such save
    assert [(r["save_id"], r["game_time"], r["last_line"]) for r in stored(pg_url)] == [(None, None, None)] * 3


def test_the_text_is_trimmed_and_one_to_two_thousand_characters(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    sent(b.feedback("  " + WORDS + "\n "))
    sent(b.feedback("x" * 2000))
    for bad in ("", "   \n ", "x" * 2001, " " + "x" * 2001, 5, None):
        refused(b.feedback(bad), 422, "invalid_decision")
    refused(b.http.post("/api/feedback", json={"text": "hi", "mood": "ok"}), 422, "invalid_decision")
    refused(b.http.post("/api/feedback", json={}), 422, "invalid_decision")
    assert [r["text"] for r in stored(pg_url)] == [WORDS, "x" * 2000]


def test_a_write_from_another_site_or_not_json_is_refused(pg_url: str, pod_a: Pod):
    r = Browser(pod_a, origin="https://evil.example").feedback(WORDS)
    assert r.status_code == 403 and r.json()["code"] == "cross_site"
    plain = Browser(pod_a).http.post("/api/feedback", content=WORDS, headers={"Content-Type": "text/plain"})
    assert plain.status_code == 415 and plain.json()["code"] == "not_json"
    assert stored(pg_url) == []


def test_five_an_hour_from_one_account_counted_across_pods(pg_url: str, pod_a: Pod, pod_b: Pod):
    b = Browser(pod_a)
    begun(b)
    for i in range(5):
        sent((b if i % 2 else b.page_on(pod_b)).feedback(f"{WORDS} {i}"))
    r = b.page_on(pod_b).feedback("one more")
    refused(r, 429, "rate_limited")
    assert len(stored(pg_url)) == 5
    other = Browser(pod_a)
    begun(other)
    sent(other.feedback(WORDS))   # another account has its own five
    sent(Browser(pod_a).feedback(WORDS))   # and so does an address with no account


def test_five_an_hour_from_one_address_with_no_account(pg_url: str, pod_a: Pod):
    here = fresh_address()
    for _ in range(5):
        sent(Browser(pod_a, here).feedback(WORDS))
    refused(Browser(pod_a, here).feedback(WORDS), 429, "rate_limited")
    sent(Browser(pod_a, fresh_address()).feedback(WORDS))
    assert len(stored(pg_url)) == 6


def test_fifty_an_hour_in_all(pg_url: str, pod_a: Pod):
    sent(Browser(pod_a).feedback(WORDS))
    with psycopg.connect(pg_url) as c:
        c.execute("INSERT INTO tries (kind, who, at) SELECT 'feedback', sha256(convert_to(i::text, 'UTF8')), now() "
                  "FROM generate_series(1, 48) AS i")
    sent(Browser(pod_a).feedback(WORDS))   # the 50th
    refused(Browser(pod_a).feedback(WORDS), 429, "rate_limited")
    assert len(stored(pg_url)) == 2


def test_feedback_over_an_hour_ago_no_longer_counts_and_account_creation_is_a_count_of_its_own(pg_url: str, pod_a: Pod):
    here = fresh_address()
    for _ in range(5):
        sent(Browser(pod_a, here).feedback(WORDS))
    rows.run(pg_url, "UPDATE tries SET at = now() - interval '61 minutes'")
    sent(Browser(pod_a, here).feedback(WORDS))
    assert rows.scalar(pg_url, "SELECT count(DISTINCT kind) FROM tries") == 1
    ok(Browser(pod_a, here).begin())   # a new account is not counted as feedback
    assert rows.scalar(pg_url, "SELECT count(*) FROM tries WHERE kind = 'feedback'") == 1


def test_a_limit_that_cannot_be_counted_refuses(pg_url: str, pod_a: Pod):
    rows.run(pg_url, "ALTER TABLE tries RENAME TO tries_gone")
    refused(Browser(pod_a).feedback(WORDS), 429, "rate_limited")
    assert stored(pg_url) == []


@pytest.fixture
def pod_no_db() -> Iterator[Pod]:
    with pod(None, "no-db") as p:
        yield p


def test_without_a_database_it_is_unavailable(pod_no_db: Pod):
    refused(Browser(pod_no_db).feedback(WORDS), 503, "save_unavailable")


def test_rows_past_the_retention_go_when_one_is_added_and_the_rest_stay(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    sent(b.feedback("first"))
    with psycopg.connect(pg_url) as c:
        for days, label in ((181, "old"), (179, "recent"), (1, "fresh")):
            c.execute("INSERT INTO feedback (created_at, text, build, release) "
                      "VALUES (now() - make_interval(days => %s), %s, 'b', 1)", (days, label))
    sent(b.feedback("second"))
    assert sorted(r["text"] for r in stored(pg_url)) == ["first", "fresh", "recent", "second"]


def test_retention_deletes_in_small_batches(pg_url: str, pod_a: Pod):
    with psycopg.connect(pg_url) as c:
        c.execute("INSERT INTO feedback (created_at, text, build, release) "
                  "SELECT now() - interval '200 days', 'old', 'b', 1 FROM generate_series(1, 30)")
    sent(Browser(pod_a).feedback(WORDS))
    assert rows.count(pg_url, "feedback") == 11   # 30 old, 20 gone, and the new one
    sent(Browser(pod_a).feedback(WORDS))
    assert rows.count(pg_url, "feedback") == 2


def test_the_text_reaches_no_log_line(pg_url: str, pod_a: Pod, capsys: pytest.CaptureFixture[str]):
    capsys.readouterr()
    b = Browser(pod_a, "203.0.113.91")
    save_id, _ = begun(b)
    sent(b.feedback(WORDS, save_id))
    refused(b.feedback(WORDS + " " + "x" * 2001), 422, "invalid_decision")
    for _ in range(4):
        sent(b.feedback(WORDS))
    refused(b.feedback(WORDS), 429, "rate_limited")
    out = capsys.readouterr().out
    assert "event=feedback.received" in out and "event=feedback.limited" in out, "no feedback line: this test is blind"
    line = next(ln for ln in out.splitlines() if "event=feedback.received" in ln)
    assert f"save={save_id}" in line and f"len={len(WORDS)}" in line and "account=" in line
    for secret in ("quokka", "third tap", "felt wrong", "203.0.113.91"):
        assert secret not in out, f"a log line carries {secret!r}"
