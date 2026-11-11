"""Two pages on one save, on two pods (CONTRACT.txt: 409 stale, SAVES ACROSS RELEASES AND PODS): a decision names the
count it follows and applies once; advances never conflict; requests on one save run one after the other."""
import threading
from typing import Any

import httpx
import pytest

from tests.api_contract import rows

from tests.api_contract.site import SET_NO_ORDERS, Browser, Pod, begun, ok, ready_tap, refused


def test_a_stale_decision_is_refused_with_the_save_as_it_is_now(pg_url: str, pod_a: Pod, pod_b: Pod):
    one = Browser(pod_a)
    save_id, s0 = begun(one)
    two = one.page_on(pod_b)
    tap = ready_tap(s0["view"])
    assert tap is not None
    assert ok(one.decide(save_id, SET_NO_ORDERS, 0))["decisions"] == 1
    rows.age_saves(pg_url, 30)   # so the stale answer's advance draws a view the last write did not
    stale = refused(two.decide(save_id, tap, 0), 409, "stale")["step"]
    assert stale is not None
    assert stale["save_id"] == save_id and stale["decisions"] == 1 and stale["build"] == pod_b.build
    assert stale["view"]["at"] >= 30
    assert all(lane["running_card"] is None for lane in stale["view"]["lanes"]), "the stale tap was applied"
    opened = ok(one.open(save_id))
    assert opened["save"]["decisions"] == 1
    assert opened["was"] == stale["view"], "the stale answer's step was not written as an advance"
    assert ok(two.decide(save_id, tap, stale["decisions"]))["decisions"] == 2   # the page carries on from it


def test_an_after_from_the_future_is_stale_too(pod_a: Pod):
    b = Browser(pod_a)
    save_id, _ = begun(b)
    assert refused(b.decide(save_id, SET_NO_ORDERS, 5), 409, "stale")["step"]["decisions"] == 0
    assert ok(b.open(save_id))["save"]["decisions"] == 0


def test_advances_never_conflict(pod_a: Pod, pod_b: Pod):
    one = Browser(pod_a)
    save_id, _ = begun(one)
    two = one.page_on(pod_b)
    ok(one.decide(save_id, SET_NO_ORDERS, 0))
    assert ok(two.advance(save_id))["decisions"] == 1
    assert ok(two.open(save_id))["step"]["decisions"] == 1
    ok(one.decide(save_id, SET_NO_ORDERS, 1))
    assert ok(two.advance(save_id))["decisions"] == 2


@pytest.fixture
def first_with_a_save(pod_a: Pod) -> tuple[Browser, Any]:
    """A browser on pod A whose first save is begun in setup: the browser and the save id."""
    first = Browser(pod_a)
    return first, begun(first)[0]


def test_racing_decisions_on_two_pods_apply_exactly_once(pod_a: Pod, pod_b: Pod,
                                                         first_with_a_save: tuple[Browser, Any]):
    first, save_id = first_with_a_save
    pages = [first.page_on(p) for p in (pod_a, pod_b, pod_a, pod_b, pod_a, pod_b)]
    deciders = pages[:4]   # the rest advance
    start = threading.Barrier(len(pages))
    answers: dict[int, httpx.Response] = {}

    def go(i: int, page: Browser) -> None:
        start.wait()
        answers[i] = page.decide(save_id, SET_NO_ORDERS, 0) if i < len(deciders) else page.advance(save_id)

    threads = [threading.Thread(target=go, args=(i, p)) for i, p in enumerate(pages)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(5)
    assert len(answers) == len(pages), "a request never answered"
    decided = [answers[i] for i in range(len(deciders))]
    assert sorted(r.status_code for r in decided) == [200, 409, 409, 409], [r.text[:200] for r in decided]
    for r in decided:
        body: dict[str, Any] = r.json()
        assert (body if r.status_code == 200 else body["step"])["decisions"] == 1
    for i in range(len(deciders), len(pages)):
        assert ok(answers[i])["decisions"] in (0, 1)
    assert ok(first.open(save_id))["save"]["decisions"] == 1
