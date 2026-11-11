"""Every POST and PUT under /api comes from this site, with a JSON body when it has one (CONTRACT.txt, ACCOUNTS AND
SESSIONS: 403 cross_site, 415 not_json). Nothing a refused write asked for happens."""
from typing import Any

import httpx
import pytest

from tests.api_contract import rows
from tests.api_contract.site import SET_NO_ORDERS, SITE, Browser, Pod, account_of, begun, ok, refused


def writes(save_id: object) -> list[tuple[str, str, dict[str, Any] | None]]:
    """Every write the contract lists: (method, path, JSON body or None)."""
    return [
        ("POST", "/api/saves", None),
        ("POST", f"/api/saves/{save_id}/open", None),
        ("POST", f"/api/saves/{save_id}/advance", None),
        ("POST", f"/api/saves/{save_id}/forecast", None),
        ("POST", f"/api/saves/{save_id}/decisions", {"decision": SET_NO_ORDERS, "after": 0}),
        ("POST", f"/api/saves/{save_id}/dry-run", {"decisions": [SET_NO_ORDERS]}),
        ("PUT", "/api/me/presentation", {"rules_opened": True}),
        ("PUT", "/api/me/settings", {"lessons": False}),
        ("PUT", f"/api/saves/{save_id}/presentation", {"lessons": ["first_mix"]}),
    ]


def send(b: Browser, method: str, path: str, body: dict[str, Any] | None, headers: dict[str, str]) -> httpx.Response:
    return b.http.request(method, path, json=body, headers=headers)


def unchanged(b: Browser) -> None:
    me = ok(b.me())
    assert me["account"] == account_of(rules_opened=False)
    assert ok(b.open(me["saves"][0]["save_id"]))["presentation"]["lessons"] == []
    assert [s["decisions"] for s in me["saves"]] == [0]


@pytest.mark.parametrize("headers", [
    {"Origin": "https://evil.example"},
    {"Origin": "https://evil.example", "Sec-Fetch-Site": "same-origin"},
    {"Origin": "null"},
    {"Origin": "https://testserver.evil.example"},
    {"Origin": "http://testserver"},
    {"Sec-Fetch-Site": "cross-site"},
    {"Sec-Fetch-Site": "same-site"},
    {},
], ids=["other-origin", "other-origin-despite-fetch-site", "null-origin", "lookalike-origin", "this-host-over-http",
         "fetch-cross-site",
        "fetch-same-site", "neither-header"])
def test_a_write_from_another_site_is_refused(pg_url: str, pod_a: Pod, headers: dict[str, str]):
    owner = Browser(pod_a)
    save_id, _ = begun(owner)
    b = Browser(pod_a, owner.address, owner.session(), origin=None)
    stranger = Browser(pod_a, origin=None)
    for method, path, body in writes(save_id):
        refused(send(b, method, path, body, headers), 403, "cross_site")
    r = send(stranger, "POST", "/api/saves", None, headers)
    refused(r, 403, "cross_site")
    assert not r.headers.get_list("set-cookie")
    unchanged(owner)
    assert len(ok(owner.me())["saves"]) == 1
    assert rows.count(pg_url, "accounts") == 1


@pytest.mark.parametrize("headers", [
    {"Origin": SITE},
    {"Sec-Fetch-Site": "same-origin"},
    {"Sec-Fetch-Site": "none"},
], ids=["origin", "fetch-same-origin", "fetch-none"])
def test_a_write_from_this_site_is_served(pod_a: Pod, headers: dict[str, str]):
    stranger = Browser(pod_a, origin=None)
    r = send(stranger, "POST", "/api/saves", None, headers)
    save_id = ok(r)["save"]["save_id"]
    ok(send(stranger, "POST", f"/api/saves/{save_id}/advance", None, headers))
    assert ok(send(stranger, "POST", f"/api/saves/{save_id}/decisions", {"decision": SET_NO_ORDERS, "after": 0},
                   headers))["decisions"] == 1


@pytest.mark.parametrize("content_type", ["text/plain", "application/x-www-form-urlencoded", "multipart/form-data"])
def test_a_body_that_is_not_json_is_refused(pod_a: Pod, content_type: str):
    b = Browser(pod_a)
    save_id, _ = begun(b)
    for method, path, body in writes(save_id):
        if body is None:
            continue
        raw = httpx.Request("GET", "/", json=body).content   # the same bytes, sent under another type
        r = b.http.request(method, path, content=raw, headers={"Content-Type": content_type})
        refused(r, 415, "not_json")
    unchanged(b)
