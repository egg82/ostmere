"""A pull request's CI stays inside its budget (docs/engineering.md, "Scope and test budget"): the longest chain of jobs a
pull request waits on, each at its `timeout-minutes`, is at most BUDGET_MIN. A job added to ci.yml must say which set it is
in, so a new job cannot join the pull-request path unseen; a timeout is the job's budget, and a job that outgrows it goes red."""
from pathlib import Path
from typing import Any

import yaml

CI = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"
BUDGET_MIN = 10
PULL_REQUEST = {"changes", "docs", "slice", "playthrough-slice", "playthrough-smoke", "tests", "shards-cover", "mutant-plants",
                "engine-bench", "pyright", "client", "app-image", "ci-ok"}
FULL_RUN = {"playthrough", "playthrough-week-one", "playthrough-week-one-saved", "playthrough-week-two", "chapter-saves",
            "chapter-saves-readings", "chapter-saves-rebased", "publish-ends"} | {
    f"chapter-saves-{route}-{link}" for route in ("typical", "sharp", "whenever") for link in "abc"}
MAIN_ONLY = {"release", "scene-art-drift"}
Jobs = dict[str, dict[str, Any]]


def jobs() -> Jobs:
    loaded: dict[str, Any] = yaml.safe_load(CI.read_text())
    return loaded["jobs"]


def needs(job: dict[str, Any]) -> list[str]:
    found = job.get("needs", [])
    return [found] if isinstance(found, str) else list(found)


Chain = tuple[int, list[str]]
NONE: Chain = (0, [])


def critical_path(all_jobs: Jobs, within: set[str]) -> Chain:
    """The longest chain of `within` jobs by timeout minutes: (minutes, the chain). A job with no timeout is 360 minutes,
    GitHub's default."""
    def longest(name: str) -> Chain:
        job = all_jobs[name]
        before: list[Chain] = [longest(n) for n in needs(job) if n in within]
        first: Chain = max(before, default=NONE)
        return first[0] + int(job.get("timeout-minutes", 360)), [*first[1], name]
    chains: list[Chain] = [longest(n) for n in within]
    return max(chains, default=NONE)


def test_every_job_is_in_a_set_and_the_pull_request_path_fits_its_budget():
    found = jobs()
    assert set(found) == PULL_REQUEST | FULL_RUN | MAIN_ONLY, \
        f"classify the job in tests/test_ci_budget.py: {sorted(set(found) ^ (PULL_REQUEST | FULL_RUN | MAIN_ONLY))}"
    assert not (PULL_REQUEST & FULL_RUN or PULL_REQUEST & MAIN_ONLY or FULL_RUN & MAIN_ONLY)
    minutes, chain = critical_path(found, PULL_REQUEST)
    assert minutes <= BUDGET_MIN, f"a pull request waits {minutes} min on {' -> '.join(chain)}; the budget is {BUDGET_MIN}"


def test_the_pull_request_path_never_waits_on_the_full_run():
    found = jobs()
    for name in PULL_REQUEST - {"ci-ok"}:   # ci-ok lists every job, and a skipped one adds no wait
        assert not set(needs(found[name])) & (FULL_RUN | MAIN_ONLY), name


def test_the_check_sees_a_chain_over_budget_and_a_job_with_no_timeout():
    found = jobs()
    slow = {**found, "tests": {**found["tests"], "timeout-minutes": BUDGET_MIN}}
    assert critical_path(slow, PULL_REQUEST)[0] > BUDGET_MIN
    bare = {**found, "pyright": {"needs": "changes"}}
    assert critical_path(bare, PULL_REQUEST)[0] > BUDGET_MIN
    assert critical_path(found, set()) == (0, [])
