"""Saves across releases and pods, and the answers that say so (CONTRACT.txt: SAVES ACROSS RELEASES AND PODS, 503
save_unavailable, X-Ashfall-Build). A newer build's save and an older rules' save are planted in the row (rows.py):
the contract names no way to stand up two builds with different rules through HTTP."""
import re
from collections.abc import Iterator
from typing import Any

import httpx
import pytest

from tests.api_contract import rows
from tests.api_contract.site import SET_NO_ORDERS, Browser, Pod, begun, ok, pod, refused

CONTRACT_PATHS = {
    ("get", "/api/content"), ("get", "/api/me"), ("post", "/api/saves"), ("post", "/api/saves/{save_id}/open"),
    ("post", "/api/saves/{save_id}/advance"), ("post", "/api/saves/{save_id}/decisions"),
    ("post", "/api/saves/{save_id}/dry-run"), ("put", "/api/me/presentation"),
}


def unavailable(r: httpx.Response) -> None:
    refused(r, 503, "save_unavailable")
    retry = r.headers.get("retry-after", "")
    assert retry.isdecimal(), f"Retry-After {retry!r} is not seconds"


def test_a_save_a_newer_build_wrote_is_unavailable_and_never_written(pg_url: str, pod_a: Pod, pod_b: Pod):
    b = Browser(pod_a)
    save_id, _ = begun(b)
    rows.from_a_newer_build(pg_url)
    before = rows.the_save_row(pg_url)
    for page in (b, b.page_on(pod_b)):
        unavailable(page.open(save_id))
        unavailable(page.advance(save_id))
        unavailable(page.decide(save_id, SET_NO_ORDERS, 0))
        unavailable(page.dry_run(save_id, [SET_NO_ORDERS]))
    assert rows.the_save_row(pg_url) == before


def test_a_save_under_older_rules_is_carried_over_under_the_current_rules(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    digest = ok(b.http.get("/api/content"))["rules_digest"]
    save_id, _ = begun(b)
    ok(b.decide(save_id, SET_NO_ORDERS, 0))
    old = rows.under_older_rules(pg_url)
    assert old != digest
    opened = ok(b.open(save_id))
    assert opened["step"]["rules_digest"] == digest
    assert opened["save"]["decisions"] == 1
    assert rows.scalar(pg_url, "SELECT rules_digest FROM saves") == digest
    assert ok(b.decide(save_id, SET_NO_ORDERS, 1))["decisions"] == 2


def test_without_a_database_saves_are_unavailable():
    with pod(None, "contract-build-nodb") as p:
        b = Browser(p, cookie="some-session-" + "y" * 30)
        unavailable(b.me())
        unavailable(b.open(1))
        unavailable(b.advance(1))
        unavailable(b.decide(1, SET_NO_ORDERS, 0))
        r = Browser(p).begin()
        assert r.status_code in (429, 503), r.text   # CONTRACT: "no database" is 503; "cannot be counted" is 429
        refused(r, r.status_code, "rate_limited" if r.status_code == 429 else "save_unavailable")
        assert not r.headers.get_list("set-cookie")


@pytest.fixture
def browser_with_a_save(pod_a: Pod) -> tuple[Browser, Any, dict[str, Any]]:
    """A browser on pod A, its first save begun in setup: the browser, the save id, the first Step."""
    b = Browser(pod_a)
    return (b, *begun(b))


def test_a_step_names_the_build_that_answered_it(pod_a: Pod, pod_b: Pod,
                                                 browser_with_a_save: tuple[Browser, Any, dict[str, Any]]):
    b, save_id, s0 = browser_with_a_save
    assert s0["build"] == pod_a.build
    r = b.page_on(pod_b).advance(save_id)
    assert ok(r)["build"] == pod_b.build == r.headers["x-ashfall-build"]
    for path in ("/api/no-such-thing", "/api/saves/1/nope"):
        assert b.http.get(path).status_code == 404   # the hook checks its headers too


@pytest.fixture
def pod_spec() -> Iterator[Pod]:
    with pod(None, "contract-build-spec") as p:
        yield p


def test_the_served_spec_holds_every_endpoint(pod_spec: Pod):
    spec: dict[str, Any] = ok(Browser(pod_spec).http.get("/openapi.json"))
    served = {(method, re.sub(r"\{[^}]*\}", "{}", path)) for path, ops in spec["paths"].items() for method in ops}
    wanted = {(method, path.replace("{save_id}", "{}")) for method, path in CONTRACT_PATHS}
    assert wanted <= served, sorted(wanted - served)
