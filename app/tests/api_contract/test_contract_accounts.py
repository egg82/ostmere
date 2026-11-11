"""Accounts and sessions (CONTRACT.txt, ACCOUNTS AND SESSIONS; GET /api/me, POST /api/saves, the presentations)."""
import httpx

from ashfall_app.saves.interface import KEPT_DAYS, MAX_SAVES
from tests.api_contract import rows
from tests.api_contract.site import (
    COOKIE, FOUR_HUNDRED_DAYS_S, Browser, Pod, account_of, begun, ok, refused, save_presentation_of,
)


def session_cookie(r: httpx.Response) -> dict[str, str] | None:
    """The Set-Cookie for the session, as {attribute: value} with the name under "" and attributes lowercased."""
    for header in r.headers.get_list("set-cookie"):
        name, _, rest = header.partition("=")
        if name.strip() == COOKIE:
            value, *attrs = rest.split(";")
            found = {"": value.strip()}
            for a in attrs:
                k, _, v = a.strip().partition("=")
                found[k.lower()] = v
            return found
    return None


def test_a_page_load_and_me_make_no_account(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    for r in (b.http.get("/"), b.me(), b.http.get("/api/content")):
        assert r.status_code == 200, (r.request.url.path, r.status_code)
        assert not r.headers.get_list("set-cookie"), r.request.url.path
    assert ok(b.me()) == {"account": None, "saves": [], "max_saves": MAX_SAVES, "kept_days": KEPT_DAYS}
    assert rows.count(pg_url, "accounts") == 0
    assert rows.count(pg_url, "sessions") == 0


def test_begin_makes_an_account_and_sets_the_session_cookie(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    r = b.begin()
    new = ok(r)
    cookie = session_cookie(r)
    assert cookie is not None, r.headers.get_list("set-cookie")
    assert cookie[""], "an empty session token"
    assert "secure" in cookie and "httponly" in cookie, cookie
    assert cookie.get("samesite", "").lower() == "none", cookie
    assert "partitioned" in cookie, cookie
    assert cookie.get("path") == "/", cookie
    assert cookie.get("max-age") == str(FOUR_HUNDRED_DAYS_S), cookie
    assert "domain" not in cookie, cookie   # a __Host- cookie names no domain
    save, step = new["save"], new["step"]
    clock = {k: save[k] for k in ("save_id", "decisions", "game_time", "ended_at")}
    assert clock == {"save_id": save["save_id"], "decisions": 0, "game_time": 0, "ended_at": None}
    assert step["save_id"] == save["save_id"]
    assert step["decisions"] == 0
    assert step["view"]["at"] == 0
    assert step["build"] == pod_a.build
    assert step["rules_digest"] == ok(b.http.get("/api/content"))["rules_digest"]
    me = ok(b.me())
    assert me["account"] == account_of(rules_opened=False)
    assert [s["save_id"] for s in me["saves"]] == [save["save_id"]]
    assert rows.count(pg_url, "accounts") == 1


def test_start_over_is_a_new_save_on_the_same_account_and_the_played_save_lists_first(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    first, _ = begun(b)
    r = b.begin()
    second = ok(r)["save"]["save_id"]
    assert second != first
    assert session_cookie(r) is None, "the session was set again within a day of being set"
    assert rows.count(pg_url, "accounts") == 1
    assert [s["save_id"] for s in ok(b.me())["saves"]] == [second, first]
    ok(b.advance(first))
    assert [s["save_id"] for s in ok(b.me())["saves"]] == [first, second]


def test_a_browser_without_a_live_session_is_no_one_until_it_begins(pg_url: str, pod_a: Pod):
    b = Browser(pod_a, cookie="forged-" + "x" * 40)
    assert ok(b.me())["account"] is None
    r = b.begin()
    ok(r)
    cookie = session_cookie(r)
    assert cookie is not None and cookie[""] != "forged-" + "x" * 40
    assert rows.count(pg_url, "accounts") == 1


def test_without_an_account_every_save_call_answers_no_account(pg_url: str, pod_a: Pod):
    owner = Browser(pod_a)
    save_id, _ = begun(owner)
    b = Browser(pod_a)
    for r in (b.open(save_id), b.advance(save_id), b.decide(save_id, {"kind": "set_orders", "orders": []}, 0),
              b.dry_run(save_id, []), b.put_me_presentation({"rules_opened": True}), b.put_me_settings({"lessons": False}),
              b.put_save_presentation(save_id, {"lessons": ["first_mix"]})):
        refused(r, 401, "no_account")
    assert rows.count(pg_url, "accounts") == 1
    assert ok(owner.me())["account"] == account_of(rules_opened=False)


def test_a_session_unused_past_400_days_is_gone(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    save_id, _ = begun(b)
    rows.age_sessions(pg_url, 401)
    assert ok(b.me())["account"] is None
    refused(b.advance(save_id), 401, "no_account")


def test_a_session_used_within_400_days_is_renewed(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    save_id, _ = begun(b)
    rows.age_sessions(pg_url, 399)
    r = b.advance(save_id)
    ok(r)
    cookie = session_cookie(r)
    assert cookie is not None and cookie.get("max-age") == str(FOUR_HUNDRED_DAYS_S), r.headers.get_list("set-cookie")
    assert rows.session_last_seen_age_s(pg_url) < 60


def test_a_session_is_renewed_at_most_once_a_day(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    save_id, step = begun(b)
    seen = rows.scalar(pg_url, "SELECT max(last_seen_at) FROM sessions")
    for r in (b.advance(save_id), b.open(save_id), b.decide(save_id, {"kind": "set_orders", "orders": []},
                                                             step["decisions"]), b.me()):
        ok(r)
        assert session_cookie(r) is None, f"{r.request.url.path} set the session again within a day"
    assert rows.scalar(pg_url, "SELECT max(last_seen_at) FROM sessions") == seen


def test_an_account_presentation_only_grows(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    assert ok(b.put_me_presentation({"devices_opened": True, "rules_opened": False})) == account_of(
        devices_opened=True, rules_opened=False)
    assert ok(b.put_me_presentation({"devices_opened": False, "rules_opened": True})) == account_of(
        devices_opened=True, rules_opened=True)
    assert ok(b.me())["account"] == account_of(devices_opened=True, rules_opened=True)


def test_an_account_presentation_from_the_build_before_is_accepted_and_its_lesson_fields_are_not_kept(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    old = {"rule_seen": True, "mix_offered": ["stand"], "lessons": ["first_mix"], "lesson_ends": [], "devices_opened": True}
    assert ok(b.put_me_presentation(old)) == account_of(devices_opened=True)
    assert ok(b.me())["account"] == account_of(devices_opened=True)
    assert b.put_me_presentation({"devices_opened": True, "no_such_field": True}).status_code == 422


def test_a_save_presentation_only_grows_and_is_that_saves_alone(pod_a: Pod):
    b = Browser(pod_a)
    first, _ = begun(b)
    second, _ = begun(b)
    assert ok(b.put_save_presentation(first, {"rule_seen": True, "lessons": ["first_mix"]})) == save_presentation_of(
        rule_seen=True, lessons=["first_mix"])
    assert ok(b.put_save_presentation(first, {"rule_seen": False, "lessons": ["first_rule"]})) == save_presentation_of(
        rule_seen=True, lessons=["first_mix", "first_rule"])
    assert ok(b.open(first))["presentation"] == save_presentation_of(rule_seen=True, lessons=["first_mix", "first_rule"])
    assert ok(b.open(second))["presentation"] == save_presentation_of()


def test_the_lessons_setting_is_replaced_whole(pod_a: Pod):
    b = Browser(pod_a)
    begun(b)
    assert ok(b.put_me_settings({"lessons": False})) == account_of(lessons=False)
    assert ok(b.me())["account"] == account_of(lessons=False)
    assert ok(b.put_me_settings({"lessons": True})) == account_of(lessons=True)


def test_one_accounts_saves_are_not_found_by_another(pod_a: Pod):
    a, b = Browser(pod_a), Browser(pod_a)
    theirs, _ = begun(a)
    mine, _ = begun(b)
    assert [s["save_id"] for s in ok(b.me())["saves"]] == [mine]
    nowhere = theirs + 10**9 if isinstance(theirs, int) else str(theirs) + "zz"
    for sid in (theirs, nowhere):
        refused(b.open(sid), 404, "not_found")
        refused(b.advance(sid), 404, "not_found")
        refused(b.decide(sid, {"kind": "set_orders", "orders": []}, 0), 404, "not_found")
        refused(b.dry_run(sid, []), 404, "not_found")
    assert ok(a.me())["saves"][0]["decisions"] == 0
