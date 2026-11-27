"""tools/nightly_verdict.py: a readouts-only red lets `release` through, and any other red still holds it. The cases
build verdicts the way the readout jobs do (`write_verdict`) and decide with the functions the workflow calls."""
import json
from pathlib import Path
from typing import Any

import yaml

from tools import nightly_verdict as nv

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def needs(**results: str) -> dict[str, dict[str, Any]]:
    return {job: {"result": r} for job, r in results.items()}


def leg(tmp: Path, job: str, index: int, total: int, status: str, changed: tuple[str, ...]) -> None:
    readouts = tmp / f"new-{job}-{index}"
    readouts.mkdir()
    for name in changed:
        (readouts / name).write_text("x\n")
    nv.write_verdict(job, index, total, status, readouts, tmp / "verdicts")


def decide(tmp: Path, n: dict[str, dict[str, Any]]) -> bool:
    return nv.readouts_only(n, nv.load_verdicts(tmp / "verdicts"))


def test_drift_only_red_is_readouts_only(tmp_path: Path):
    leg(tmp_path, "playthrough", 0, 2, "success", ("dayone-typical.txt",))
    leg(tmp_path, "playthrough", 1, 2, "success", ())
    leg(tmp_path, "playthrough-week-two", 0, 1, "success", ("weektwo-eight-sharp.txt",))
    n = needs(playthrough="failure", **{"playthrough-week-two": "failure"}, tests="success", changes="success", publish_ends="skipped")
    assert decide(tmp_path, n)


def test_a_failed_test_in_a_drifting_job_is_a_real_failure(tmp_path: Path):
    leg(tmp_path, "playthrough", 0, 2, "failure", ("dayone-typical.txt",))
    leg(tmp_path, "playthrough", 1, 2, "success", ())
    assert not decide(tmp_path, needs(playthrough="failure"))


def test_a_red_job_with_no_verdict_is_a_real_failure(tmp_path: Path):
    leg(tmp_path, "playthrough", 0, 1, "success", ("dayone-typical.txt",))
    n = needs(playthrough="failure", tests="failure")
    assert not decide(tmp_path, n)
    assert not decide(tmp_path, needs(playthrough="failure", **{"chapter-saves": "cancelled"}))


def test_a_matrix_leg_that_never_reported_is_a_real_failure(tmp_path: Path):
    leg(tmp_path, "playthrough", 0, 2, "success", ("dayone-typical.txt",))
    assert not decide(tmp_path, needs(playthrough="failure"))


def test_a_red_with_nothing_changed_and_a_green_run_are_not_readouts_only(tmp_path: Path):
    leg(tmp_path, "playthrough", 0, 1, "failure", ())
    assert not decide(tmp_path, needs(playthrough="failure"))
    assert not decide(tmp_path, needs(playthrough="success"))


def test_the_nightly_refreshes_only_when_nothing_else_is_red():
    assert nv.refresh("true", "success", "success")
    assert not nv.refresh("true", "failure", "success")
    assert not nv.refresh("true", "success", "failure")
    assert not nv.refresh("false", "success", "success")
    assert not nv.refresh("", "success", "success")


def run_nightly(tmp: Path, full_only: str, deep: str) -> Path:
    out = tmp / "nightly"
    nv.main(["decide", "--full-only", full_only, "--deep", deep, "--health", "success", "--run", "42", "--out", str(out)])
    return out


def test_release_holds_unless_green_or_readouts_only(tmp_path: Path):
    assert not nv.held("success", "42", tmp_path)
    assert not nv.held("", "", tmp_path)
    assert nv.held("failure", "42", tmp_path / "no-artifact")
    assert nv.held("failure", "42", run_nightly(tmp_path, "false", "success"))
    assert nv.held("failure", "42", run_nightly(tmp_path, "true", "failure"))
    only = run_nightly(tmp_path, "true", "success")
    assert not nv.held("failure", "42", only)
    assert nv.held("failure", "43", only), "a verdict is for its own run"


def test_release_check_exit_codes(tmp_path: Path):
    only = run_nightly(tmp_path, "true", "success")
    assert nv.main(["held", "--conclusion", "failure", "--run", "42", "--verdict", str(only)]) == 0
    assert nv.main(["held", "--conclusion", "failure", "--run", "42", "--verdict", str(tmp_path / "none")]) == 1


def test_verdict_end_to_end_through_the_cli(tmp_path: Path, capsys: Any):
    readouts = tmp_path / "readouts-new"
    readouts.mkdir()
    (readouts / "dayone-typical.txt").write_text("x\n")
    nv.main(["verdict", "--job", "playthrough", "--index", "0", "--total", "1", "--status", "success", "--readouts", str(readouts), "--out", str(tmp_path / "v")])
    nv.main(["verdict", "--job", "tests", "--status", "failure", "--readouts", str(tmp_path / "absent"), "--out", str(tmp_path / "v")])
    (tmp_path / "needs.json").write_text(json.dumps(needs(playthrough="failure")))
    assert nv.main(["readouts-only", "--needs", str(tmp_path / "needs.json"), "--verdicts", str(tmp_path / "v")]) == 0
    assert capsys.readouterr().out == "only=true\n"
    (tmp_path / "needs.json").write_text(json.dumps(needs(playthrough="failure", tests="failure")))
    nv.main(["readouts-only", "--needs", str(tmp_path / "needs.json"), "--verdicts", str(tmp_path / "v")])
    assert capsys.readouterr().out == "only=false\n"


def test_body_lists_ids_only():
    text = nv.body(["app/tests/readouts/dayone-typical.txt", "app/tests/readouts/opening.txt"])
    assert "- `dayone-typical`\n- `opening`\n" in text and "app/tests" not in text


def test_every_job_that_fails_on_drift_records_its_verdict_first():
    jobs: dict[str, Any] = yaml.safe_load((WORKFLOWS / "ci.yml").read_text())["jobs"]
    drifting = {name: job for name, job in jobs.items() if any("readout differs" in str(s.get("name", "")) for s in job["steps"])}
    assert len(drifting) >= 7
    for name, job in drifting.items():
        uses = [i for i, s in enumerate(job["steps"]) if s.get("uses") == "./.github/actions/readout-verdict"]
        fails = [i for i, s in enumerate(job["steps"]) if "readout differs" in str(s.get("name", ""))]
        assert uses and uses[0] < fails[0], name
        assert job["steps"][fails[0]]["uses"] == "./.github/actions/readout-differs", name
        assert job["steps"][uses[0]]["if"] == "always()", name
    assert "refresh-readouts" in yaml.safe_load((WORKFLOWS / "nightly.yml").read_text())["jobs"]


def run_report(tmp: Path, event: str, changed: tuple[str, ...]) -> tuple[int, str]:
    tmp.mkdir()
    readouts = tmp / "readouts-new"
    readouts.mkdir()
    for name in changed:
        (readouts / name).write_text("x\n")
    summary = tmp / "summary.md"
    code = nv.report(event, "42", readouts, summary)
    return code, summary.read_text() if summary.exists() else ""


def test_a_differing_readout_is_listed_and_fails_unless_on_a_pull_request(tmp_path: Path):
    code, summary = run_report(tmp_path / "pr", "pull_request", ("dayone-typical.txt",))
    assert code == 0 and "`dayone-typical.txt`" in summary and "readouts_pull 42" in summary
    for event in ("push", "schedule", "workflow_dispatch"):
        code, summary = run_report(tmp_path / event, event, ("dayone-typical.txt",))
        assert code == 1 and "`dayone-typical.txt`" in summary, event


def test_nothing_differing_reports_nothing_on_any_event(tmp_path: Path):
    for event in ("pull_request", "push"):
        assert run_report(tmp_path / event, event, ()) == (0, "")


def test_a_test_failure_still_fails_a_pull_request_job():
    jobs: dict[str, Any] = yaml.safe_load((WORKFLOWS / "ci.yml").read_text())["jobs"]
    for name, job in jobs.items():
        steps = job["steps"]
        if not any(s.get("uses") == "./.github/actions/readout-differs" for s in steps):
            continue
        tests = [s for s in steps if "pytest" in str(s.get("run", ""))]
        assert tests and all("continue-on-error" not in s and "|| true" not in s["run"] for s in tests), name
