"""tools/ci_costs.py, the refresh of tools/ci_costs.json from the chapter_saves jobs' logs.

tests/fixtures/ci_costs holds what `gh` returned for nightly run 45869030021: the `event=chapter_saves.*` lines (and a few
noise lines) of three of its jobs (a route's first link, a rebased group, a readings part; log-<job id>.txt, `gh api
repos/OWNER/NAME/actions/jobs/<id>/logs`), its jobs as the tool lists them (jobs-45869030021.jsonl) and the newest run ids of
the two workflows (runs-*.jsonl). The run's other jobs have no log here and read as empty. That run predates the `index=`
field of a reading line, so the one reading line with an index is the captured line with the field added, in the test."""
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
RUN = 45869030021
LINKS, REBASED, READINGS = "140079379069", "140085183022", "140085183341"


def log(job: str) -> str:
    return (FIXTURES / f"log-{job}.txt").read_text()


class Stub:
    """`gh` over the captured files; a job with no captured log has an empty one. Records the paths it was asked for."""

    def __init__(self, logs: dict[str, str] | None = None) -> None:
        self.asked: list[str] = []
        self.logs = logs or {}

    def __call__(self, args: list[str]) -> str:
        path = next((a for a in args if a.startswith("repos/")), "")
        self.asked.append(path)
        if m := re.fullmatch(r"repos/o/r/actions/workflows/(\w+)\.yml/runs", path):
            return (FIXTURES / ("runs-ci.jsonl" if m[1] == "ci" else "runs-nightly.jsonl")).read_text()
        if path == f"repos/o/r/actions/runs/{RUN}/jobs":
            return (FIXTURES / f"jobs-{RUN}.jsonl").read_text()
        if re.fullmatch(r"repos/o/r/actions/runs/\d+/jobs", path):
            return ""
        if m := re.fullmatch(r"repos/o/r/actions/jobs/(\d+)/logs", path):
            captured = FIXTURES / f"log-{m[1]}.txt"
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
    stub = Stub()
    assert ci_costs.refresh(ci_costs.GitHub("o/r", stub), [RUN], 40, path) == 0
    out = capsys.readouterr().out
    assert f"event=ci_costs.run run={RUN} jobs=38 measured=11" in out and "event=ci_costs.finish" in out
    unmeasured = next(line for line in out.splitlines() if line.startswith("event=ci_costs.unmeasured"))
    assert "ends:sharp:eighteen" in unmeasured and "ends:sharp:week1" not in unmeasured and "readings:eight:0-13" in unmeasured
    written = saves_plan.load(path)
    assert written["ends"]["sharp"]["week1"] == 49 and written["ends"]["sharp"]["eighteen"] == 180
    assert written["source_runs"] == [RUN] and json.loads(path.read_text()) == written
    _, chains, reb, reads = today_inputs()
    assert problems_of(written, chains, reb, reads) == []
    assert not saves_plan.plan(written, chains, reb, reads).estimated


def problems_of(table: dict[str, Any], chains: dict[str, list[str]], reb: list[str], reads: list[str]) -> list[str]:
    return saves_plan.problems(saves_plan.plan(table, chains, reb, reads))


def test_a_cost_jump_in_the_table_is_what_saves_plans_check_reports(tmp_path: Path):
    path = table_copy(tmp_path)
    log_text = f"event=chapter_saves.player chapter=eight route=typical cpu_s={saves_plan.TARGET_S + 100}.0\n"
    stub = Stub({LINKS: log_text})
    assert ci_costs.refresh(ci_costs.GitHub("o/r", stub), [RUN], 40, path) == 0
    _, chains, reb, reads = today_inputs()
    found = problems_of(saves_plan.load(path), chains, reb, reads)
    assert len(found) == 1 and found[0].startswith("typical-")


def test_with_no_run_ids_the_newest_runs_that_measured_something_are_read_and_the_ids_are_recorded(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path = table_copy(tmp_path)
    stub = Stub()
    assert ci_costs.refresh(ci_costs.GitHub("o/r", stub), [], 40, path) == 0
    asked = [p for p in stub.asked if p.endswith("/jobs")]
    assert asked[0].startswith("repos/o/r/actions/runs/45945307701") and f"repos/o/r/actions/runs/{RUN}/jobs" in asked
    assert saves_plan.load(path)["source_runs"] == [RUN]
    assert capsys.readouterr().out.count("event=ci_costs.run ") == 6


def test_no_measurement_leaves_the_table_untouched_and_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path = table_copy(tmp_path)
    before = path.read_text()
    assert ci_costs.refresh(ci_costs.GitHub("o/r", Stub({LINKS: "", REBASED: "", READINGS: ""})), [45945307701], 40, path) == 1
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
