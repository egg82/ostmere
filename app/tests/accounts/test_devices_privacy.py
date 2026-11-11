"""What moving to another device keeps out of the logs, and how it behaves under two redeems at once and a write from
another site; and that the build before migration 0004 still writes its rows on the new schema."""
import threading
from collections.abc import Iterator

import psycopg
import pytest

from ashfall_app import logs
from tests.accounts.devices import JOIN_KEY, SITE, Browser, Site, code_of, site


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def test_no_log_line_holds_a_code_words_a_hash_a_token_or_the_address(s: Site, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    capsys.readouterr()
    a, b = Browser(s, "203.0.113.41"), Browser(s, "203.0.113.42")
    a.play()
    code = code_of(a.code())
    said = a.words().json()["words"]
    b.play()
    assert b.join(code).status_code == 409
    assert b.join(said).status_code == 409
    assert Browser(s, "203.0.113.43").join(code).status_code == 200
    assert Browser(s, "203.0.113.44").join(said.upper()).status_code == 200
    assert Browser(s, "203.0.113.45").join(code).status_code == 404
    assert Browser(s, "203.0.113.46").join("zebra-zebra-zebra-zebra").status_code == 404
    out = capsys.readouterr().out
    assert "event=join.ok" in out and "event=transfer.made" in out and "event=words.made" in out, "blind: no lines"
    assert "reason=confirm_needed" in out and "reason=no_such_code" in out
    with s.db.connect() as c:
        hashes = [bytes(v) for (v,) in c.exec_driver_sql(
            "SELECT code_hash FROM transfer_codes UNION ALL SELECT words_hash FROM accounts WHERE words_hash IS NOT"
            " NULL UNION ALL SELECT token_hash FROM sessions UNION ALL SELECT who FROM tries")]
    assert len([h for h in hashes if len(h) >= 32]) >= 4, "too few hashes read: the probe saw nothing"
    planted = [code, code.replace("-", ""), said, said.upper(), "zebra", a.session() or "?", b.session() or "?",
               "203.0.113.4", JOIN_KEY.hex()]
    planted += [h.hex() for h in hashes if len(h) >= 32] + [h[3:].hex() for h in hashes if len(h) >= 32]
    for i, secret in enumerate(planted):
        assert secret not in out, f"a log line holds planted secret #{i}"


def test_two_redeems_of_one_code_at_once_join_one_browser(s: Site):
    a = Browser(s)
    a.play()
    code = code_of(a.code())
    browsers = [Browser(s) for _ in range(6)]
    got: list[int] = []
    def redeem(b: Browser) -> None:
        got.append(b.join(code).status_code)

    threads = [threading.Thread(target=redeem, args=(b,)) for b in browsers]
    for th in threads:
        th.start()
    for th in threads:
        th.join(10)
    assert sorted(got) == [200] + [404] * 5


def test_a_write_from_another_site_is_refused_and_not_cached(s: Site):
    a = Browser(s)
    a.begin()
    for path, body in (("/api/me/transfer-code", None), ("/api/me/words", None), ("/api/join", {"typed": "x"})):
        r = a.http.post(path, json=body, headers={"Origin": "https://evil.example"})
        assert r.status_code == 403 and r.json()["code"] == "cross_site" and r.headers["cache-control"] == "no-store"
        r = a.http.post(path, content=b"typed=x", headers={"Origin": SITE, "Content-Type": "text/plain"})
        assert r.status_code == 415 and r.json()["code"] == "not_json"
    assert s.scalar("SELECT count(*) FROM transfer_codes") == 0


def test_the_build_before_0004_writes_its_rows_on_the_new_schema(pg_url: str):
    """Expand only: the inserts the previous build makes (no words, no codes) still go in."""
    with psycopg.connect(pg_url) as c:
        acc = c.execute("INSERT INTO accounts (created_at, last_seen_at) VALUES (now(), now()) RETURNING id").fetchone()
        assert acc is not None
        c.execute("INSERT INTO sessions (account_id, token_hash, created_at, last_seen_at) VALUES (%s, 'x', now(),"
                  " now())", (acc[0],))
        row = c.execute("SELECT words_hash, words_made_at, presentation FROM accounts").fetchone()
    assert row == (None, None, {})
