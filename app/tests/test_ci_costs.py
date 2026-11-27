"""tools/ci_costs.py, the refresh of tools/ci_costs.json from the chapter_saves jobs' logs.

tests/fixtures/ci_costs holds what `gh` returned (`gh api repos/OWNER/NAME/actions/jobs/<id>/logs`, trimmed to the
`event=chapter_saves.*` and `event=saves_plan.*` lines, log-<job id>.txt):
- run 45869030021, a nightly: three jobs' logs (a route's first link, a rebased group, a readings part), for the parse tests;
- run 45934206912, a full run (a pull request labelled `playthroughs`): its job list as the tool lists them, the `saves-plan`
  job's log and three save jobs' logs; the run's other jobs have no log here and read as empty;
- run 45945307701, a slice run: its job list, whose save jobs were all skipped;
- runs-*.jsonl, run ids as the two workflows' run lists give them, picked from the real lists.
That nightly predates the `index=` field of a reading line, so the one reading line with an index is the captured line with
the field added, in the test. A made-up run id in a test (the Stub's `alias`) is named in the test's docstring."""
import json
import math
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.test_saves_plan import today_inputs
from tools import ci_costs, saves_plan

FIXTURES = Path(__file__).parent / "fixtures" / "ci_costs"
RUN, SLICE = 45934206912, 45945307701
LINKS, REBASED, READINGS = "140079379069", "140085183022", "140085183341"
COPIES = (5 * 10**11, 6 * 10**11)
LINK1, LINK2, REBASED_JOB = "140296503396", "140300375419", "140307617711"


def log(job: str) -> str:
    return (FIXTURES / f"log-{job}.txt").read_text()


class Stub:
    """`gh` over the captured files; a job with no captured log has an empty one. `alias` makes run B a copy of run A's job
    list with every job id moved by B (its logs are A's, unless `logs` has the moved id), and `drop` removes the jobs
    whose name has the word given for it (`drop`, by run). Records the paths it was asked for."""

    def __init__(self, logs: dict[str, str] | None = None, alias: dict[int, int] | None = None, drop: dict[int, str] | None = None) -> None:
        self.asked: list[str] = []
        self.logs = logs or {}
        self.alias = alias or {}
        self.drop = drop or {}
        self.moved: dict[int, int] = {}

    def jobs(self, run: int) -> str:
        source = self.alias.get(run, run)
        path = FIXTURES / f"jobs-{source}.jsonl"
        text = path.read_text() if path.exists() else ""
        if source == run:
            return text
        rows = [json.loads(line) for line in text.splitlines()]
        self.moved.update({r["id"] + run: r["id"] for r in rows})
        return "".join(json.dumps({**r, "id": r["id"] + run}) + "\n" for r in rows if self.drop.get(run, "\0") not in r["name"])

    def __call__(self, args: list[str]) -> str:
        path = next((a for a in args if a.startswith("repos/")), "")
        self.asked.append(path)
        if m := re.fullmatch(r"repos/o/r/actions/workflows/(\w+)\.yml/runs", path):
            ids = (FIXTURES / ("runs-ci.jsonl" if m[1] == "ci" else "runs-nightly.jsonl")).read_text()
            return ids + "".join(json.dumps({"id": b}) + "\n" for b in self.alias) * (m[1] == "ci")
        if m := re.fullmatch(r"repos/o/r/actions/runs/(\d+)/jobs", path):
            return self.jobs(int(m[1]))
        if m := re.fullmatch(r"repos/o/r/actions/jobs/(\d+)/logs", path):
            job = int(m[1])
            captured = FIXTURES / f"log-{self.moved.get(job, job)}.txt"
            return self.logs[m[1]] if m[1] in self.logs else captured.read_text() if captured.exists() else ""
        raise AssertionError(path)


def table_copy(tmp_path: Path) -> Path:
    target = tmp_path / "ci_costs.json"
    target.write_text(saves_plan.TABLE.read_text())
    return target


def test_a_links_log_gives_each_end_by_route_and_chapter_rounded_up():
    found = ci_costs.parse(log(LINKS))
    assert found == {("ends", "sharp", c): s for c, s in
                     [("week1", 49), ("eight", 19), ("nine", 17), ("eleven", 17), ("twelve", 106), ("fifteen", 63), ("sixteen", 61)]}


def test_a_rebased_log_gives_each_chapter():
    assert ci_costs.parse(log(REBASED)) == {("rebased", "eight"): 19, ("rebased", "nine"): 31, ("rebased", "eleven"): 37,
                                            ("rebased", "twelve"): 60}


def test_a_reading_is_placed_by_its_index_and_a_line_without_one_is_left_out():
    lines = log(READINGS)
    assert "event=chapter_saves.reading" in lines and ci_costs.parse(lines) == {}
    first = next(line for line in lines.splitlines() if "event=chapter_saves.reading" in line)
    indexed = first.replace("chapter=eighteen ", "chapter=eighteen index=4 ")
    assert ci_costs.parse(indexed) == {("readings", "eighteen", 4): math.ceil(float(first.rsplit("cpu_s=", 1)[1]))}


def test_a_chapter_played_twice_in_one_log_counts_its_costlier_play():
    twice = "event=chapter_saves.player chapter=a route=r cpu_s=5.1\nevent=chapter_saves.player chapter=a route=r cpu_s=9.0\n"
    assert ci_costs.parse(twice) == {("ends", "r", "a"): 9}


def test_the_cost_is_the_max_over_the_runs_not_the_last_or_the_mean():
    runs = [{("ends", "r", "a"): 10, ("rebased", "a"): 7}, {("ends", "r", "a"): 30}, {("ends", "r", "a"): 20, ("rebased", "a"): 9}]
    assert ci_costs.worst(runs) == {("ends", "r", "a"): 30, ("rebased", "a"): 9}


def test_a_chapter_no_run_measured_keeps_its_old_cost_and_is_listed_not_zeroed_or_dropped():
    table = json.loads(saves_plan.TABLE.read_text())
    new, unmeasured, unplaced = ci_costs.merge(table, {("ends", "sharp", "eight"): 777}, [3, 1, 2])
    assert new["ends"]["sharp"]["eight"] == 777 and new["source_runs"] == [1, 2, 3]
    assert new["ends"]["sharp"]["nine"] == table["ends"]["sharp"]["nine"] > 0
    assert new["rebased"] == table["rebased"] and new["readings"] == table["readings"]
    assert ("ends", "sharp", "nine") in unmeasured and ("ends", "sharp", "eight") not in unmeasured
    assert len(unmeasured) == len(ci_costs.table_keys(table)) - 1 and unplaced == []
    assert new["job_overhead_s"] == table["job_overhead_s"]


def test_hand_written_estimates_stay_marked_until_a_run_measures_them():
    table = json.loads(saves_plan.TABLE.read_text())
    table["estimated"] = {"rows": ["ends:sharp:eight", "ends:sharp:nine"], "basis": "by hand"}
    new, _, _ = ci_costs.merge(table, {("ends", "sharp", "eight"): 777}, [1])
    assert new["estimated"] == {"rows": ["ends:sharp:nine"], "basis": "by hand"}
    every = {k: 1 for k in ci_costs.table_keys(table)}
    assert "estimated" not in ci_costs.merge(table, every, [1])[0]


def test_a_new_chapter_is_added_and_a_reading_with_no_step_in_the_table_is_reported_not_added():
    table = json.loads(saves_plan.TABLE.read_text())
    steps = len(table["readings"]["eight"]["steps_s"])
    measured = {("ends", "sharp", "newchapter"): 12, ("readings", "eight", steps): 30, ("readings", "newchapter", 0): 30}
    new, _, unplaced = ci_costs.merge(table, measured, [1])
    assert new["ends"]["sharp"]["newchapter"] == 12
    assert new["readings"] == table["readings"] and sorted(unplaced) == [("readings", "eight", steps), ("readings", "newchapter", 0)]


def test_the_unmeasured_figures_are_derived_from_the_table_and_the_committed_ones_are_what_the_rule_gives():
    table = json.loads(saves_plan.TABLE.read_text())
    assert ci_costs.unmeasured_row(table, table["unmeasured"]["basis"]) == table["unmeasured"]
    table["ends"]["typical"]["eight"] = 4000
    assert ci_costs.unmeasured_row(table, "")["ends"]["typical"] == 5000


def test_the_written_table_reads_back_through_saves_plan_and_plans_every_job_within_its_cap(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path = table_copy(tmp_path)
    assert ci_costs.refresh(ci_costs.GitHub("o/r", Stub()), [RUN], 40, path) == 0
    out = capsys.readouterr().out
    assert f"event=ci_costs.run run={RUN} full=true jobs=68 measured=18" in out and "event=ci_costs.finish" in out
    unmeasured = next(line for line in out.splitlines() if line.startswith("event=ci_costs.unmeasured"))
    assert "ends:sharp:twentythree" in unmeasured and "ends:sharp:week1" not in unmeasured and "readings:eight:0-13" in unmeasured
    written = saves_plan.load(path)
    assert written["ends"]["sharp"]["week1"] == 42 and written["ends"]["sharp"]["nineteen"] == 203
    assert written["source_runs"] == [RUN] and json.loads(path.read_text()) == written
    _, chains, reb, reads = today_inputs()
    assert problems_of(written, chains, reb, reads) == []
    assert not saves_plan.plan(written, chains, reb, reads).estimated


def problems_of(table: dict[str, Any], chains: dict[str, list[str]], reb: list[str], reads: list[str]) -> list[str]:
    return saves_plan.problems(saves_plan.plan(table, chains, reb, reads))


def test_a_cost_jump_in_the_table_is_what_saves_plans_check_reports(tmp_path: Path):
    path = table_copy(tmp_path)
    log_text = f"event=chapter_saves.player chapter=eight route=typical cpu_s={saves_plan.TARGET_S + 100}.0\n"
    assert ci_costs.refresh(ci_costs.GitHub("o/r", Stub({LINK1: log_text})), [RUN], 40, path) == 0
    _, chains, reb, reads = today_inputs()
    found = problems_of(saves_plan.load(path), chains, reb, reads)
    assert len(found) == 1 and found[0].startswith("typical-")


def test_by_default_only_full_runs_are_read_a_slice_run_is_skipped_and_the_ids_are_recorded(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path = table_copy(tmp_path)
    stub = Stub(alias=dict.fromkeys(COPIES, RUN))
    assert ci_costs.refresh(ci_costs.GitHub("o/r", stub), [], 40, path) == 0
    out = capsys.readouterr().out
    assert f"event=ci_costs.run run={SLICE} full=false jobs=32 measured=0" in out
    assert f"event=ci_costs.run run={RUN} full=true" in out and out.count("event=ci_costs.run ") == 5
    assert saves_plan.load(path)["source_runs"] == sorted([RUN, *COPIES])
    slice_jobs = {str(json.loads(line)["id"]) for line in (FIXTURES / f"jobs-{SLICE}.jsonl").read_text().splitlines()}
    assert not [p for p in stub.asked if p.rsplit("/", 2)[-2] in slice_jobs and p.endswith("/logs")], "a skipped run's logs are not fetched"


def test_a_run_missing_one_planned_save_job_is_not_full_whatever_it_logged(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Run 7e11 is the full run's job list without its `rebased-eight` job (a made-up run, to stand for one that ran a part);
    5e11 and 6e11 are the full run again, so three full runs exist."""
    path = table_copy(tmp_path)
    huge = f"event=chapter_saves.player chapter=eight route=typical cpu_s={saves_plan.TARGET_S}.0\n"
    stub = Stub({str(int(LINK1) + 7 * 10**11): huge}, alias={7 * 10**11: RUN, **dict.fromkeys(COPIES, RUN)}, drop={7 * 10**11: "rebased-eight"})
    assert ci_costs.refresh(ci_costs.GitHub("o/r", stub), [], 40, path) == 0
    out = capsys.readouterr().out
    assert f"run={7 * 10**11} full=false" in out and f"run={RUN} full=true" in out
    assert saves_plan.load(path)["source_runs"] == sorted([RUN, *COPIES])
    assert saves_plan.load(path)["ends"]["typical"]["eight"] == json.loads(saves_plan.TABLE.read_text())["ends"]["typical"]["eight"]


def test_a_key_only_some_of_the_full_runs_measured_takes_their_max_and_is_named_partial(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Runs 5e11 and 6e11 are the full run again (made-up ids, job ids moved); 5e11's first link cached all but its first two
    chapters."""
    path = table_copy(tmp_path)
    two = "".join(log(LINK1).splitlines(keepends=True)[:2]).replace("cpu_s=41.3", "cpu_s=90.0")
    stub = Stub({str(int(LINK1) + COPIES[0]): two}, alias=dict.fromkeys(COPIES, RUN))
    assert ci_costs.refresh(ci_costs.GitHub("o/r", stub), [], 40, path) == 0
    out = capsys.readouterr().out
    written = saves_plan.load(path)
    assert written["source_runs"] == sorted([RUN, *COPIES])
    assert written["ends"]["sharp"]["week1"] == 90 and written["ends"]["sharp"]["eight"] == 17, "the max of the runs that had it"
    partial = next(line for line in out.splitlines() if line.startswith("event=ci_costs.partial"))
    assert partial.startswith("event=ci_costs.partial of=3 keys=") and "ends:sharp:nine" in partial and "ends:sharp:week1" not in partial
    assert "partial=" in out and "partial=0" not in out


def test_fewer_than_three_full_runs_leave_the_table_alone_and_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path = table_copy(tmp_path)
    before = path.read_text()
    assert ci_costs.refresh(ci_costs.GitHub("o/r", Stub(alias={5 * 10**11: RUN})), [], 40, path) == 1
    assert path.read_text() == before and "found 2 of the 3 full runs" in capsys.readouterr().err


def test_no_measurement_leaves_the_table_untouched_and_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path = table_copy(tmp_path)
    before = path.read_text()
    blank = {LINK1: "", LINK2: "", REBASED_JOB: "", "140307617745": ""}
    assert ci_costs.refresh(ci_costs.GitHub("o/r", Stub(blank)), [RUN], 40, path) == 1
    assert path.read_text() == before and "measured=0" in capsys.readouterr().err


def test_dry_run_writes_nothing(tmp_path: Path):
    path = table_copy(tmp_path)
    before = path.read_text()
    assert ci_costs.refresh(ci_costs.GitHub("o/r", Stub()), [RUN], 40, path, write=False) == 0
    assert path.read_text() == before


def test_the_committed_table_says_how_it_was_measured_in_the_tools_words():
    assert saves_plan.load()["measured"] == ci_costs.MEASURED


def test_the_nightly_refreshes_the_table_without_failing_the_nightly_and_commits_it_with_the_readouts():
    nightly = Path(__file__).parents[2] / ".github" / "workflows" / "nightly.yml"
    job = yaml.safe_load(nightly.read_text())["jobs"]["refresh-readouts"]
    refresh = [s for s in job["steps"] if "tools.ci_costs" in s.get("run", "")]
    assert len(refresh) == 1 and refresh[0]["continue-on-error"] is True
    commit = [s for s in job["steps"] if "git add" in s.get("run", "")]
    assert len(commit) == 1 and "app/tools/ci_costs.json" in commit[0]["run"] and "app/tests/readouts" in commit[0]["run"]
    assert job["steps"].index(refresh[0]) < job["steps"].index(commit[0])
    assert job["env"]["GH_TOKEN"] and job["permissions"]["actions"] == "read"
    assert "needs.full.result" not in job["if"], "the table is refreshed whether or not the nightly's readouts differ"
