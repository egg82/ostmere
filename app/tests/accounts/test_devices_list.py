"""Your devices (api/CONTRACT.txt, "Your devices"): an account lists its sessions and ends one, which signs that
browser out. Through the app on a database of the test's own."""
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import select

from ashfall_app.db.tables import sessions
from tests.accounts.devices import Browser, Site, code_of, site

FIREFOX = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
IPHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
          "Version/17.5 Mobile/15E148 Safari/604.1")


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def two_browsers(s: Site) -> tuple[Browser, Browser]:
    """A holds an account with a session labelled Firefox on Linux; B joined it from an iPhone."""
    a, b = Browser(s), Browser(s)
    a.http.headers["User-Agent"] = FIREFOX
    b.http.headers["User-Agent"] = IPHONE
    a.begin()
    assert b.join(code_of(a.code())).status_code == 200
    return a, b


def listed(b: Browser) -> list[dict[str, Any]]:
    r = b.http.get("/api/me/devices")
    assert r.status_code == 200, r.text
    found: list[dict[str, Any]] = r.json()["devices"]
    return found


def signed_out(b: Browser) -> bool:
    """The browser's next request has no account: /api/me answers none, and a route that needs one answers 401."""
    gone = b.http.get("/api/me/devices")
    assert gone.status_code in (200, 401), gone.text
    return gone.status_code == 401 and b.me()["account"] is None and gone.json()["code"] == "no_account"


def test_the_list_shows_each_browser_of_the_account_and_marks_the_asker(s: Site):
    a, b = two_browsers(s)
    seen_by_a, seen_by_b = listed(a), listed(b)
    assert [d["label"] for d in seen_by_a] == ["Firefox on Linux", "Safari on iPhone"]
    assert [d["label"] for d in seen_by_b] == ["Safari on iPhone", "Firefox on Linux"]
    assert [d["this_device"] for d in seen_by_a] == [True, False]
    assert [d["this_device"] for d in seen_by_b] == [True, False]
    assert {d["device_id"] for d in seen_by_a} == {d["device_id"] for d in seen_by_b}


def test_a_row_carries_no_token_and_no_hash(s: Site):
    a, b = two_browsers(s)
    r = a.http.get("/api/me/devices")
    assert set(r.json()["devices"][0]) == {"device_id", "label", "created_at", "last_seen_at", "this_device"}
    with s.db.connect() as c:
        hashes = [bytes(h).hex() for h in c.execute(select(sessions.c.token_hash)).scalars()]
    tokens = [a.session() or "", b.session() or ""]
    assert all(h not in r.text for h in hashes) and all(t and t not in r.text for t in tokens)


def test_the_list_holds_only_the_askers_account(s: Site):
    a, _ = two_browsers(s)
    stranger = Browser(s)
    stranger.http.headers["User-Agent"] = "curl/8"
    stranger.begin()
    assert len(listed(stranger)) == 1 and listed(stranger)[0]["label"] == "A browser"
    assert len(listed(a)) == 2
    ids_a = {d["device_id"] for d in listed(a)}
    assert listed(stranger)[0]["device_id"] not in ids_a


def test_the_list_needs_an_account(s: Site):
    r = Browser(s).http.get("/api/me/devices")
    assert r.status_code == 401 and r.json()["code"] == "no_account"
    assert r.headers["cache-control"] == "no-store"


def test_removing_a_device_signs_that_browser_out(s: Site):
    a, b = two_browsers(s)
    there = next(d["device_id"] for d in listed(a) if not d["this_device"])
    assert not signed_out(b)
    r = a.http.delete(f"/api/me/devices/{there}")
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store", r.text
    assert [d["this_device"] for d in r.json()["devices"]] == [True]
    assert signed_out(b)
    assert not signed_out(a)   # the browser that removed it is still in


def test_removing_this_device_signs_it_out_and_ends_its_cookie(s: Site):
    a, b = two_browsers(s)
    mine = next(d["device_id"] for d in listed(a) if d["this_device"])
    r = a.http.delete(f"/api/me/devices/{mine}")
    assert r.status_code == 200, r.text
    assert r.headers["set-cookie"].startswith('__Host-ashfall_session=""') and "Max-Age=0" in r.headers["set-cookie"]
    assert [d["this_device"] for d in r.json()["devices"]] == [False]
    assert signed_out(a)
    assert not signed_out(b)


def test_a_session_of_another_account_cannot_be_removed(s: Site):
    a, _ = two_browsers(s)
    stranger = Browser(s)
    stranger.begin()
    theirs = listed(stranger)[0]["device_id"]
    r = a.http.delete(f"/api/me/devices/{theirs}")
    assert r.status_code == 404 and r.json()["code"] == "not_found"
    assert not signed_out(stranger) and len(listed(stranger)) == 1
    nothing = a.http.delete("/api/me/devices/999999999")
    assert nothing.status_code == 404 and nothing.json() == r.json()   # exactly as a device that does not exist


def test_removing_a_device_needs_an_account_and_an_origin(s: Site):
    a, _ = two_browsers(s)
    there = next(d["device_id"] for d in listed(a) if not d["this_device"])
    r = Browser(s).http.delete(f"/api/me/devices/{there}")
    assert r.status_code == 401 and r.headers["cache-control"] == "no-store"
    cross = a.http.delete(f"/api/me/devices/{there}", headers={"Origin": "https://evil.example"})
    assert cross.status_code == 403 and cross.json()["code"] == "cross_site"
    assert len(listed(a)) == 2


def test_a_removed_device_can_join_again_and_is_a_new_row(s: Site):
    a, b = two_browsers(s)
    there = next(d["device_id"] for d in listed(a) if not d["this_device"])
    assert a.http.delete(f"/api/me/devices/{there}").status_code == 200
    b.http.cookies.clear()
    assert b.join(code_of(a.code())).status_code == 200
    ids = {d["device_id"] for d in listed(a)}
    assert len(ids) == 2 and there not in ids


def test_listing_and_removing_write_nothing_to_a_session(s: Site):
    a, _ = two_browsers(s)
    s.clock.tick(days=2)
    with s.db.connect() as c:
        before = sorted(c.execute(select(sessions.c.id, sessions.c.last_seen_at)).all())
    r = a.http.get("/api/me/devices")
    assert "set-cookie" not in r.headers
    there = next(d["device_id"] for d in listed(a) if not d["this_device"])
    r = a.http.delete(f"/api/me/devices/{there}")
    assert "set-cookie" not in r.headers
    with s.db.connect() as c:
        after = sorted(c.execute(select(sessions.c.id, sessions.c.last_seen_at)).all())
    assert [x for x in after] == [x for x in before if x[0] != there]
