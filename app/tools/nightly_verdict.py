#!/usr/bin/env python3
"""Tell a nightly that is red only because readouts drifted from one that is really red (issue #573).

Standard library only: the workflow runs it without installing anything. Subcommands, each a step of the workflow:

  verdict      a readout job's own record (.github/actions/readout-verdict): did every step before the drift step
               succeed, and which readouts changed. Written as JSON under --out.
  readouts-only  ci-ok's decision from `toJSON(needs)` and the downloaded verdicts: prints `only=true` or `only=false`.
  decide       the nightly's decision from the called workflow's `only` and the other nightly jobs' results: prints
               `refresh=true|false`, and writes the nightly's verdict file when true.
  held         `release`'s check: exit 1 (hold) unless the last nightly succeeded or left a readouts-only verdict.
  body         the refresh pull request's body from changed paths on stdin.

A red job is a drift-only red when every verdict of that job exists (one per matrix leg), each says its tests passed,
and at least one lists a changed readout. Anything else that is red, including a job with no verdict, is a real failure.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any

VERDICT_FILE = "nightly-verdict.json"
RED = {"failure", "cancelled", "timed_out"}
Record = dict[str, Any]


def write_verdict(job: str, index: int, total: int, status: str, readouts: Path, out: Path) -> Path:
    names = sorted(p.name for p in readouts.rglob("*") if p.is_file()) if readouts.is_dir() else []
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{job}-{index}.json"
    target.write_text(json.dumps({"job": job, "index": index, "total": total, "tests_ok": status == "success", "changed": names}))
    return target


def load_verdicts(directory: Path) -> dict[str, list[Record]]:
    found: dict[str, list[Record]] = {}
    for f in sorted(directory.rglob("*.json")) if directory.is_dir() else []:
        v = json.loads(f.read_text())
        found.setdefault(v["job"], []).append(v)
    return found


def drift_only(legs: list[Record]) -> bool:
    """True when `legs` are every leg of one job, all with passing tests, and some readout changed."""
    if not legs or len({v["index"] for v in legs}) != len(legs) or len(legs) != legs[0]["total"]:
        return False
    return all(v["tests_ok"] for v in legs) and any(v["changed"] for v in legs)


def readouts_only(needs: dict[str, Record], verdicts: dict[str, list[Record]]) -> bool:
    red = [job for job, n in needs.items() if n["result"] in RED]
    return bool(red) and all(drift_only(verdicts.get(job, [])) for job in red)


def refresh(full_only: str, deep: str, health: str) -> bool:
    return full_only == "true" and deep == "success" and health == "success"


def held(conclusion: str, run_id: str, directory: Path) -> bool:
    """Whether `release` holds for the last completed nightly (its conclusion, run id, and downloaded verdict dir)."""
    if conclusion != "failure":
        return False
    f = directory / VERDICT_FILE
    if not f.is_file():
        return True
    v = json.loads(f.read_text())
    return not (v.get("readouts_only") is True and str(v.get("run")) == run_id)


def body(paths: list[str]) -> str:
    ids = sorted(Path(p).stem for p in paths if p.endswith(".txt"))
    return "Readouts that differ from their committed text, pulled from the nightly's `readouts-new-*` artifacts:\n\n" + "".join(f"- `{i}`\n" for i in ids)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verdict")
    v.add_argument("--job", required=True)
    v.add_argument("--index", type=int, default=0)
    v.add_argument("--total", type=int, default=1)
    v.add_argument("--status", required=True)
    v.add_argument("--readouts", type=Path, required=True)
    v.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("readouts-only")
    r.add_argument("--needs", type=Path, required=True)
    r.add_argument("--verdicts", type=Path, required=True)
    d = sub.add_parser("decide")
    d.add_argument("--full-only", default="")
    d.add_argument("--deep", default="")
    d.add_argument("--health", default="")
    d.add_argument("--run", required=True)
    d.add_argument("--out", type=Path, required=True)
    h = sub.add_parser("held")
    h.add_argument("--conclusion", default="")
    h.add_argument("--run", default="")
    h.add_argument("--verdict", type=Path, required=True)
    sub.add_parser("body")
    a = ap.parse_args(argv)
    if a.cmd == "verdict":
        write_verdict(a.job, a.index, a.total, a.status, a.readouts, a.out)
    elif a.cmd == "readouts-only":
        print(f"only={str(readouts_only(json.loads(a.needs.read_text()), load_verdicts(a.verdicts))).lower()}")
    elif a.cmd == "decide":
        go = refresh(a.full_only, a.deep, a.health)
        if go:
            a.out.mkdir(parents=True, exist_ok=True)
            (a.out / VERDICT_FILE).write_text(json.dumps({"run": a.run, "readouts_only": True}))
        print(f"refresh={str(go).lower()}")
    elif a.cmd == "held":
        if held(a.conclusion, a.run, a.verdict):
            print(f"HOLDING: the last nightly on main ({a.conclusion or 'none'}, run {a.run or '-'}) failed for more than readouts.", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(body(sys.stdin.read().split()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
