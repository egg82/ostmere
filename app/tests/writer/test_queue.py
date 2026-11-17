"""The writer's queue and daily budget (docs/decisions/writer.md, layer 4): a job over the world's allowance or the
global budget is answered with its stand-in and a logged reason; a world's share grows with its returning days up to
a cap; a world whose player has not come back queues nothing; counts start over each day."""
import logging
from datetime import date, timedelta

import pytest

from ashfall_app.writer import budget as budgets
from ashfall_app.writer.interface import JobKind
from ashfall_app.writer.queue import Job, Queue
from ashfall_app.writer.service import Registry, Writer
from tests.kills import kills

KIND = JobKind("arrival")


class Counting:
    def __init__(self) -> None:
        self.calls = 0

    def write(self, kind: JobKind, stand_in: str) -> str:
        self.calls += 1
        return "written"


class Today:
    def __init__(self) -> None:
        self.day = date(2026, 11, 16)

    def __call__(self) -> date:
        return self.day


def make(budget: budgets.Budget) -> tuple[Queue, Counting, Today]:
    client, today = Counting(), Today()
    return Queue(Writer(Registry((KIND,)), client), today, budget), client, today


def job(save: str = "a") -> Job:
    return Job(save, "arrival", "stand-in")


def lines(caplog: pytest.LogCaptureFixture, event: str) -> list[dict[str, object]]:
    return [getattr(r, "fields") for r in caplog.records if r.getMessage() == event and hasattr(r, "fields")]


def run(q: Queue, n: int, save: str = "a") -> list[str]:
    for _ in range(n):
        assert q.enqueue(job(save))
    return [text for _, text in q.drain()]


@kills(1)
def test_a_job_over_the_save_cap_is_answered_with_the_stand_in_and_logged(caplog: pytest.LogCaptureFixture) -> None:
    q, client, _ = make(budgets.Budget(global_daily=100, per_save_daily=2, weight_cap=8))
    q.visit("a", 0)
    with caplog.at_level(logging.INFO, logger="ashfall.writer"):
        assert run(q, 3) == ["written", "written", "stand-in"]
    assert client.calls == 2
    [skip] = lines(caplog, "writer.job.skip")
    assert skip["reason"] == "save_cap" and skip["kind"] == "arrival" and skip["save_spent"] == 2


@kills(2)
def test_a_job_over_the_global_budget_is_answered_with_the_stand_in_and_logged(caplog: pytest.LogCaptureFixture) -> None:
    q, client, _ = make(budgets.Budget(global_daily=3, per_save_daily=100, weight_cap=8))
    q.visit("a", 0)
    with caplog.at_level(logging.INFO, logger="ashfall.writer"):
        assert run(q, 4) == ["written"] * 3 + ["stand-in"]
    assert client.calls == 3
    [skip] = lines(caplog, "writer.job.skip")
    assert skip["reason"] == "global_cap" and skip["global_spent"] == 3


def test_every_run_is_logged_without_the_save_id_or_the_stand_in(caplog: pytest.LogCaptureFixture) -> None:
    q, _, _ = make(budgets.DEFAULT)
    q.visit("a-save-id", 0)
    with caplog.at_level(logging.INFO, logger="ashfall.writer"):
        q.enqueue(Job("a-save-id", "arrival", "the stand-in line"))
        q.drain()
    [ran] = lines(caplog, "writer.job.run")
    assert ran["reason"] == "ok" and ran["global_spent"] == 1
    assert "a-save-id" not in str(ran) and "stand-in line" not in str(ran)


@kills(3)
def test_a_world_that_came_back_more_days_gets_a_bigger_share() -> None:
    b = budgets.Budget(global_daily=12, per_save_daily=100, weight_cap=8)
    q, _, _ = make(b)
    q.visit("old", 3)
    q.visit("new", 0)
    assert run(q, 12, "old").count("written") == 9   # 12 * 4 / 5, rounded down
    assert run(q, 12, "new").count("written") == 2   # 12 * 1 / 5, rounded down


@kills(4)
def test_the_share_stops_growing_at_the_cap() -> None:
    b = budgets.Budget(global_daily=100, per_save_daily=100, weight_cap=4)
    assert budgets.weight(b, 3) == budgets.weight(b, 300) == 4
    assert budgets.weight(b, 0) == 1 and budgets.weight(b, 1) == 2


def test_more_worlds_mean_smaller_shares() -> None:
    b = budgets.Budget(global_daily=12, per_save_daily=100, weight_cap=8)
    assert budgets.allowance(b, 1, [1]) == 12
    assert budgets.allowance(b, 1, [1, 1, 1]) == 4
    assert budgets.allowance(b, 1, []) == 0


@kills(5)
def test_a_world_whose_player_has_not_come_back_queues_nothing(caplog: pytest.LogCaptureFixture) -> None:
    q, client, _ = make(budgets.DEFAULT)
    with caplog.at_level(logging.INFO, logger="ashfall.writer"):
        assert q.enqueue(job("gone")) is False
    assert q.drain() == [] and client.calls == 0
    [skip] = lines(caplog, "writer.job.skip")
    assert skip["reason"] == "abandoned"


def test_counts_start_over_the_next_day() -> None:
    q, _, today = make(budgets.Budget(global_daily=100, per_save_daily=1, weight_cap=8))
    q.visit("a", 0)
    assert run(q, 2) == ["written", "stand-in"]
    today.day += timedelta(days=1)
    assert not q.enqueue(job()), "yesterday's visit does not carry over"
    q.visit("a", 0)
    assert run(q, 1) == ["written"]
