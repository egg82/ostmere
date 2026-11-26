"""tools/ci_health.py on responses captured from this repository's own runs (tests/fixtures/ci_health: `gh api` output as the
script reads it): the wall clock of its pull-request runs, the runs that passed on a rerun after failing a test job, and the
one issue per kind it opens or updates. The forge is a stub of `gh` that serves those files and records what it was asked."""
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools import ci_health

FIXTURES = Path(__file__).parent / "fixtures" / "ci_health"
NOW = datetime(2026, 11, 26, 6, 0, tzinfo=timezone.utc)
TESTS = re.compile(r"^(tests|playthrough|chapter-saves)")
RERUN = 45733640625
"""The captured run whose first attempt failed `tests (c)` (a test killed by pytest-timeout) and whose second passed."""


class Stub:
    """`gh` over the captured files; issue commands are recorded, and `issue list` finds `existing` if given."""

    def __init__(self, existing: int | None = None) -> None:
        self.existing = existing
        self.issued: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        path = next((a for a in args if a.startswith("repos/")), "")
        if path.endswith("/actions/runs"):
            return (FIXTURES / "runs.jsonl").read_text()
        if m := re.fullmatch(r"repos/o/r/actions/runs/(\d+)/attempts/(\d+)/jobs", path):
            return (FIXTURES / f"jobs-{m[1]}-{m[2]}.jsonl").read_text()
        if m := re.fullmatch(r"repos/o/r/actions/jobs/(\d+)/logs", path):
            return (FIXTURES / f"log-{m[1]}.txt").read_text()
        if args[:2] == ["issue", "list"]:
            return '[{"number": %d}]' % self.existing if self.existing else "[]"
        self.issued.append(args)
        return "https://github.com/o/r/issues/77\n" if args[:2] == ["issue", "create"] else ""


def runs() -> list[ci_health.Run]:
    return ci_health.GitHub("o/r", Stub()).pr_runs(NOW.replace(day=19), "CI")


def test_a_run_is_its_created_to_updated_wall_clock_and_the_wanted_workflow():
    found = {r.id: r for r in runs()}
    assert len(found) == 9 and found[RERUN].attempt == 2 and found[RERUN].conclusion == "success"
    assert round(found[RERUN].wall_min, 1) == 10.2
    assert ci_health.GitHub("o/r", Stub()).pr_runs(NOW, "no such workflow") == []


def test_the_median_and_worst_are_of_the_successful_runs_only():
    stats = ci_health.median_worst(runs())
    assert stats is not None and (round(stats[0], 1), round(stats[1], 1)) == (36.8, 129.6)
    assert ci_health.median_worst([r for r in runs() if r.conclusion != "success"]) is None


def test_only_a_run_whose_first_attempt_failed_a_test_job_and_that_passed_later_is_a_rerun():
    found = ci_health.reruns(ci_health.GitHub("o/r", Stub()), runs(), TESTS)
    assert [(r.id, [j.name for j in jobs]) for r, jobs in found] == [(RERUN, ["tests (c)"])]
    # the other reruns that passed failed only `ci-ok` in their first attempt, the rest of it cancelled by a newer push
    assert {r.id for r in runs() if r.attempt > 1 and r.conclusion == "success"} == {RERUN, 45734977711, 45652019545}


def test_a_test_killed_by_the_timeout_and_a_failed_test_are_named():
    rerun = ci_health.GitHub("o/r", Stub()).failed_jobs(runs()[1], 1, TESTS)[0]
    assert ci_health.failing_tests(rerun.log) == \
        ["tests/opening/test_feature_effects.py::test_a_feature_carries_the_cost_text_and_changes_of_its_answer (timeout)"]
    assert ci_health.failing_tests((FIXTURES / "log-tail-139701557225.txt").read_text()) == [
        "tests/test_doc_citations.py::test_the_citations_resolve",
        "tests/test_gates_command.py::test_the_script_runs_every_gate_in_the_table",
        "tests/test_suppressions.py::test_the_held_ledger_is_what_the_code_is"]
    assert ci_health.failing_tests("all green") == []


def test_a_teardown_error_names_its_test():
    """pytest reports a teardown failure, the per-test time ceiling's among them, as ERROR, not FAILED."""
    log = "ERROR tests/test_x.py::test_slow - tests/test_x.py::test_slow took 4.20s of wall clock\n"
    assert ci_health.failing_tests(log) == ["tests/test_x.py::test_slow"]


def test_a_rerun_opens_one_issue_and_over_the_budget_another(capsys: pytest.CaptureFixture[str]):
    stub = Stub()
    ci_health.run(ci_health.GitHub("o/r", stub), 10, 7, "CI", TESTS, False, NOW)
    creates = [a for a in stub.issued if a[:2] == ["issue", "create"]]
    assert [a[a.index("--label") + 1] for a in creates] == ["ci-health-budget", "ci-health-reruns"]
    assert "tests (c)" in creates[1][creates[1].index("--body") + 1] and "median 36.8 min" in creates[0][creates[0].index("--body") + 1]
    assert "reruns_passed=1" in capsys.readouterr().out


def test_an_open_issue_is_updated_not_duplicated():
    stub = Stub(existing=41)
    ci_health.run(ci_health.GitHub("o/r", stub), 10, 7, "CI", TESTS, False, NOW)
    assert [a[:3] for a in stub.issued if a[:2] == ["issue", "edit"]] == [["issue", "edit", "41"]] * 2
    assert not [a for a in stub.issued if a[:2] == ["issue", "create"]]


def test_within_budget_with_no_rerun_prints_one_line_and_opens_nothing(capsys: pytest.CaptureFixture[str]):
    stub = Stub()
    ci_health.run(ci_health.GitHub("o/r", stub), 100, 7, "CI", re.compile("^no test job$"), False, NOW)
    assert stub.issued == []
    assert capsys.readouterr().out.strip() == ("event=ci_health days=7 pr_runs=6 median_min=36.8 worst_min=129.6 budget_min=100 "
                                               "reruns_passed=0 issues=none")


def test_a_clean_night_closes_each_open_issue(capsys: pytest.CaptureFixture[str]):
    stub = Stub(existing=41)
    ci_health.run(ci_health.GitHub("o/r", stub), 100, 7, "CI", re.compile("^no test job$"), False, NOW)
    assert [a[:3] for a in stub.issued] == [["issue", "close", "41"]] * 2
    assert "issues=budget closed #41;reruns closed #41" in capsys.readouterr().out


def test_a_window_with_no_passing_run_closes_nothing():
    """No passing run means the median is unknown, not back under budget, and no run at all is no evidence of no rerun."""
    stub = Stub(existing=41)
    ci_health.run(ci_health.GitHub("o/r", stub), 100, 7, "no such workflow", TESTS, False, NOW)
    assert stub.issued == []
