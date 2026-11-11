"""A save is written by the server on every decision and advance; open answers it as the player last saw it, its past
lines and the time away (CONTRACT.txt: Step, ENDPOINTS). The wall clock is moved by ageing the save's row (rows.py)."""
import random
from typing import Any

import pytest

from tests.api_contract import rows
from tests.api_contract.site import SET_NO_ORDERS, Browser, Pod, begun, busy_tap, ok, ready_tap, refused

Line = tuple[int, str]


def lines_of(step: dict[str, Any]) -> list[Line]:
    """A Step's lines as (at, key), after checking (at, seq) strictly rises within it."""
    keys = [(ln["at"], ln["seq"]) for ln in step["lines"]]
    assert keys == sorted(set(keys)), f"lines not in unique (at, seq) order: {keys}"
    return [(ln["at"], ln["key"]) for ln in step["lines"]]


def history_of(opened: dict[str, Any]) -> list[Line]:
    ns = [p["n"] for p in opened["history"]]
    assert ns == sorted(set(ns)), f"history not oldest first by n: {ns}"
    assert len(ns) <= 200
    return [(p["at"], p["key"]) for p in opened["history"]]


def follows(earlier: list[Line], later: list[Line]) -> None:
    if earlier and later:
        assert later[0][0] >= earlier[-1][0], f"a later Step's lines start before an earlier one's end: {earlier[-1]} {later[0]}"


def is_step(step: dict[str, Any], save_id: object, pod: Pod, digest: str) -> None:
    assert step["save_id"] == save_id
    assert step["build"] == pod.build
    assert step["rules_digest"] == digest
    assert isinstance(step["decisions"], int)


def test_a_decision_then_a_reload_draws_the_same_view_and_lines(pg_url: str, pod_a: Pod, pod_b: Pod):
    b = Browser(pod_a)
    digest = ok(b.http.get("/api/content"))["rules_digest"]
    save_id, s0 = begun(b)
    tap = ready_tap(s0["view"])
    assert tap is not None, "the first view offers no ready card"
    s1 = ok(b.decide(save_id, tap, s0["decisions"]))
    is_step(s1, save_id, pod_a, digest)
    assert s1["decisions"] == 1
    rows.age_saves(pg_url, 40)   # forty seconds pass: the tap lands
    s2 = ok(b.advance(save_id))
    assert s2["view"]["at"] >= 40
    rows.age_saves(pg_url, 20)   # the page is shut for twenty seconds before the reload
    seen = lines_of(s0) + lines_of(s1) + lines_of(s2)
    assert seen, "forty seconds after a tap wrote no line: nothing to compare"
    for a, c in ((s0, s1), (s1, s2)):
        follows(lines_of(a), lines_of(c))
    reload = Browser(pod_b, b.address, b.session())   # the page reloads, onto the other pod
    opened = ok(reload.open(save_id))
    assert opened["save"]["save_id"] == save_id and opened["save"]["decisions"] == 1
    assert opened["was"] == s2["view"]
    assert history_of(opened) == seen
    is_step(opened["step"], save_id, pod_b, digest)
    assert opened["step"]["view"]["at"] >= s2["view"]["at"] + 20
    again = ok(b.open(save_id))
    assert again["was"] == opened["step"]["view"]
    assert history_of(again) == seen + lines_of(opened["step"])


@pytest.fixture
def browser_with_a_save(pod_a: Pod) -> tuple[Browser, Any]:
    """A browser whose first save is begun in setup: the browser and the save id."""
    b = Browser(pod_a)
    return b, begun(b)[0]


def test_the_time_away_runs_and_game_time_never_runs_back(pg_url: str, browser_with_a_save: tuple[Browser, Any]):
    b, save_id = browser_with_a_save
    rows.age_saves(pg_url, 100)
    s = ok(b.advance(save_id))
    assert 100 <= s["view"]["at"] < 160
    assert ok(b.me())["saves"][0]["game_time"] == s["view"]["at"]
    rows.age_saves(pg_url, -1000)   # the row now claims it began in the future
    assert ok(b.advance(save_id))["view"]["at"] >= s["view"]["at"]
    assert ok(b.open(save_id))["step"]["view"]["at"] >= s["view"]["at"]


def test_a_dry_run_writes_nothing(pod_a: Pod):
    b = Browser(pod_a)
    save_id, s0 = begun(b)
    tap = ready_tap(s0["view"])
    assert tap is not None
    after = ok(b.dry_run(save_id, [tap]))
    assert any(lane["running_card"] == tap["card"] for lane in after["lanes"]), after["lanes"]
    opened = ok(b.open(save_id))
    assert opened["save"]["decisions"] == 0
    assert opened["was"] == s0["view"]
    assert all(lane["running_card"] is None for lane in opened["step"]["view"]["lanes"])
    refused(b.dry_run(save_id, [{"kind": "tap_card", "card": "no-such-card"}]), 422, "invalid_decision")


def test_a_decision_the_rules_refuse_is_invalid_and_not_applied(pod_a: Pod):
    b = Browser(pod_a)
    save_id, s0 = begun(b)
    tap = ready_tap(s0["view"])
    assert tap is not None
    s1 = ok(b.decide(save_id, tap, 0))
    busy = busy_tap(s1["view"])
    assert busy is not None, "a tap that left no lane busy"
    refused(b.decide(save_id, busy, 1), 422, "invalid_decision")
    refused(b.decide(save_id, {"kind": "tap_card", "card": "no-such-card"}, 1), 422, "invalid_decision")
    refused(b.decide(save_id, {"kind": "no_such_kind"}, 1), 422, "invalid_decision")
    refused(b.http.post(f"/api/saves/{save_id}/decisions", json={"decision": SET_NO_ORDERS}), 422, "invalid_decision")
    refused(b.http.post(f"/api/saves/{save_id}/decisions", json={"decision": SET_NO_ORDERS, "after": 1, "x": 1}),
            422, "invalid_decision")
    assert ok(b.open(save_id))["save"]["decisions"] == 1
    assert ok(b.decide(save_id, SET_NO_ORDERS, 1))["decisions"] == 2


class Model:
    """What the page has been told: the decision count, the last view written, every line, in order."""

    def __init__(self, step: dict[str, Any]) -> None:
        self.decisions: int = step["decisions"]
        self.view: dict[str, Any] | None = step["view"]
        self.lines: list[Line] = lines_of(step)
        self.exact = True   # every line written has been seen (false once a 422's advance may have written some)

    def wrote(self, step: dict[str, Any]) -> None:
        new = lines_of(step)
        follows(self.lines, new)
        self.lines += new
        self.view = step["view"]
        assert step["decisions"] == self.decisions


def one_move(rng: random.Random, b: Browser, save_id: object, m: Model, url: str) -> None:
    move = rng.choice(["decide", "tap", "busy", "bogus", "stale", "advance", "dry", "age", "open"])
    if m.view is None:
        m.wrote(ok(b.advance(save_id)))
    view = m.view
    assert view is not None
    if move == "age":
        rows.age_saves(url, rng.randint(1, 30))
    elif move == "advance":
        m.wrote(ok(b.advance(save_id)))
    elif move == "dry":
        ok(b.dry_run(save_id, [SET_NO_ORDERS]))
    elif move == "stale":
        if m.decisions:
            m.wrote(refused(b.decide(save_id, SET_NO_ORDERS, m.decisions - 1), 409, "stale")["step"])
    elif move == "open":
        opened = ok(b.open(save_id))
        if m.view is not None:
            assert opened["was"] == m.view
        history = history_of(opened)
        assert history == m.lines[-200:] if m.exact else set(m.lines) <= set(history)
        assert opened["save"]["decisions"] == m.decisions
        m.wrote(opened["step"])
    else:
        decision = {"decide": SET_NO_ORDERS, "tap": ready_tap(view), "busy": busy_tap(view),
                    "bogus": {"kind": "tap_card", "card": "no-such-card"}}[move] or SET_NO_ORDERS
        r = b.decide(save_id, decision, m.decisions)
        if r.status_code == 422:
            refused(r, 422, "invalid_decision")
            m.view, m.exact = None, False
            return
        m.decisions += 1
        m.wrote(ok(r))


@pytest.mark.parametrize("seed", range(6))
def test_any_sequence_of_moves_reloads_to_what_the_page_last_drew(pg_url: str, pod_a: Pod, seed: int):
    rng = random.Random(seed)
    b = Browser(pod_a)
    save_id, s0 = begun(b)
    m = Model(s0)
    for _ in range(7):
        one_move(rng, b, save_id, m, pg_url)
    final = ok(b.advance(save_id))
    m.wrote(final)
    rows.age_saves(pg_url, 5)
    opened = ok(b.open(save_id))
    assert opened["was"] == final["view"]
    assert opened["save"]["decisions"] == m.decisions
    if m.exact:
        assert history_of(opened) == m.lines[-200:]
