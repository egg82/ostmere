#!/usr/bin/env python3
"""Refresh tools/ci_costs.json, the table the chapter-save jobs are planned from (tools/saves_plan.py), from CI's own logs.

Run from app/: python -m tools.ci_costs [run-id ...] [--repo OWNER/NAME] [--scan N] [--table PATH] [--dry-run]

The chapter_saves jobs log `cpu_s` for each end, rebased save and heavy-step reading they play (tools/chapter_saves.py). With
no run ids, the newest runs of ci.yml and nightly.yml are read, newest first, until three have a job that played something
(a run whose saves were all cached logs nothing to measure); --scan bounds how many runs are looked at. Each job's log is
fetched once. The new table holds, per measured end (route and chapter), rebased chapter and reading step, the max over those
runs, rounded up to whole seconds. Anything no run measured keeps its old value and is listed as unmeasured, never dropped or
zeroed; `job_overhead_s` and each reading row's `setup_s` (no job logs them) are kept. The `unmeasured` figures are derived
again from the table (`unmeasured_row`).

Standard library only: the nightly runs it with no install (it needs GH_TOKEN with actions: read).
"""
import argparse
import copy
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

TABLE = Path(__file__).with_name("ci_costs.json")
WORKFLOWS = ("ci.yml", "nightly.yml")
WANTED = 3
MEASURED = ("max over the last three runs that played chapter saves of the per-chapter cpu_s the chapter_saves jobs log; "
            "refreshed by tools/ci_costs.py")
LINE = re.compile(r"event=chapter_saves\.(player|rebased|reading)\s(.*)")
Key = tuple[Any, ...]
"""("ends", route, chapter), ("rebased", chapter) or ("readings", chapter, step index)."""
Gh = Callable[[list[str]], str]


def gh_cli(args: list[str]) -> str:
    done = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if done.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])} failed: {done.stderr.strip()[-300:]}")
    return done.stdout


def parse(log: str) -> dict[Key, int]:
    """The cost of each end, rebased save and reading a job's log reports, in whole seconds rounded up (the highest if a key
    repeats). A reading line with no `index=` (logged before it was) is not placed in the table and is left out."""
    found: dict[Key, int] = {}
    for line in log.splitlines():
        m = LINE.search(line)
        if not m:
            continue
        kind, fields = m[1], dict(re.findall(r"(\w+)=(\S+)", m[2]))
        if "cpu_s" not in fields:
            continue
        if kind == "player":
            key: Key = ("ends", fields["route"], fields["chapter"])
        elif kind == "rebased":
            key = ("rebased", fields["chapter"])
        elif "index" in fields:
            key = ("readings", fields["chapter"], int(fields["index"]))
        else:
            continue
        found[key] = max(found.get(key, 0), math.ceil(float(fields["cpu_s"])))
    return found


def worst(runs: list[dict[Key, int]]) -> dict[Key, int]:
    """The max of each key over `runs`."""
    out: dict[Key, int] = {}
    for run in runs:
        for key, seconds in run.items():
            out[key] = max(out.get(key, 0), seconds)
    return out


def table_keys(table: dict[str, Any]) -> list[Key]:
    keys: list[Key] = [("ends", route, c) for route, by in table["ends"].items() for c in by]
    keys += [("rebased", c) for c in table["rebased"]]
    keys += [("readings", c, i) for c, row in table["readings"].items() for i in range(len(row["steps_s"]))]
    return keys


def names(keys: list[Key]) -> str:
    """`keys` as logfmt text: ends and rebased saves one by one, a chapter's reading steps as index runs ("readings:eight:0-13")."""
    out = [":".join(k) for k in keys if k[0] != "readings"]
    steps: dict[str, list[int]] = {}
    for _, chapter, i in (k for k in keys if k[0] == "readings"):
        steps.setdefault(chapter, []).append(i)
    for chapter, indexes in steps.items():
        runs: list[list[int]] = []
        for i in sorted(indexes):
            if runs and i == runs[-1][-1] + 1:
                runs[-1].append(i)
            else:
                runs.append([i])
        out += [f"readings:{chapter}:{r[0]}" + (f"-{r[-1]}" if len(r) > 1 else "") for r in runs]
    return ",".join(out)


def more(seconds: int) -> int:
    """`seconds` and a quarter, rounded up."""
    return -(-seconds * 5 // 4)


def unmeasured_row(table: dict[str, Any], basis: str) -> dict[str, Any]:
    """The figures for a chapter with no row: the costliest measured one plus a quarter, per route's end, the rebased save,
    and the readings setup and heavy step, at the step count of the chapter with the most reading time."""
    rows = table["readings"].values()
    longest = max(rows, key=lambda r: r["setup_s"] + sum(r["steps_s"]))
    return {"ends": {route: more(max(by.values())) for route, by in table["ends"].items()},
            "rebased": more(max(table["rebased"].values())),
            "readings": {"setup_s": more(max(r["setup_s"] for r in rows)),
                         "steps_s": [more(max(max(r["steps_s"]) for r in rows))] * len(longest["steps_s"])},
            "basis": basis}


def merge(table: dict[str, Any], measured: dict[Key, int], runs: list[int]) -> tuple[dict[str, Any], list[Key], list[Key]]:
    """(the new table, the keys of the old one nothing measured, the measured readings the table has no step for). A chapter
    or route the table lacks is added for an end or rebased save; a reading is only ever placed in an existing row, whose
    `setup_s` nothing logs."""
    new = copy.deepcopy(table)
    unplaced: list[Key] = []
    for key, seconds in sorted(measured.items()):
        if key[0] == "ends":
            new["ends"].setdefault(key[1], {})[key[2]] = seconds
        elif key[0] == "rebased":
            new["rebased"][key[1]] = seconds
        elif key[1] in new["readings"] and key[2] < len(new["readings"][key[1]]["steps_s"]):
            new["readings"][key[1]]["steps_s"][key[2]] = seconds
        else:
            unplaced.append(key)
    new["measured"] = MEASURED
    new["source_runs"] = sorted(runs)
    new["unmeasured"] = unmeasured_row(new, table["unmeasured"]["basis"])
    return new, [k for k in table_keys(table) if k not in measured], unplaced


class GitHub:
    """The forge calls, over `gh` (a function serving captured responses stands in for it in a test)."""

    def __init__(self, repo: str, gh: Gh = gh_cli) -> None:
        self.repo, self.gh = repo, gh

    def lines(self, path: str, jq: str, *fields: str, paginate: bool = True) -> list[dict[str, Any]]:
        out = self.gh(["api", "-X", "GET", f"repos/{self.repo}/{path}", *fields, *(["--paginate"] if paginate else []), "--jq", jq])
        return [json.loads(line) for line in out.splitlines() if line.strip()]

    def recent_runs(self, scan: int) -> list[int]:
        """The newest `scan` run ids of the workflows that run the chapter saves, newest first (ids rise with time)."""
        ids = [r["id"] for w in WORKFLOWS
               for r in self.lines(f"actions/workflows/{w}/runs", ".workflow_runs[]|{id}", "-f", f"per_page={scan}", paginate=False)]
        return sorted(set(ids), reverse=True)[:scan]

    def saves_jobs(self, run: int) -> list[int]:
        """The ids of the run's chapter-save jobs that finished successfully."""
        jobs = self.lines(f"actions/runs/{run}/jobs", ".jobs[]|{id,name,conclusion}", "-f", "per_page=100")
        return [j["id"] for j in jobs if "chapter-saves" in j["name"] and j["conclusion"] == "success"]

    def log(self, job: int) -> str:
        return self.gh(["api", f"repos/{self.repo}/actions/jobs/{job}/logs"])


def read_run(forge: GitHub, run: int) -> tuple[int, dict[Key, int]]:
    """(the run's chapter-save jobs, the worst cost of each key they log)."""
    jobs = forge.saves_jobs(run)
    return len(jobs), worst([parse(forge.log(j)) for j in jobs])


def collect(forge: GitHub, ids: list[int], scan: int) -> tuple[list[int], list[dict[Key, int]]]:
    """The runs read and what each measured: `ids` as given, else the newest runs, newest first, that measured anything,
    until WANTED."""
    used: list[int] = []
    costs: list[dict[Key, int]] = []
    for run in ids or forge.recent_runs(scan):
        jobs, found = read_run(forge, run)
        print(f"event=ci_costs.run run={run} jobs={jobs} measured={len(found)}", flush=True)
        if found:
            used.append(run)
            costs.append(found)
        if not ids and len(used) == WANTED:
            break
    return used, costs


def refresh(forge: GitHub, ids: list[int], scan: int, path: Path, write: bool = True) -> int:
    table = json.loads(path.read_text())
    print(f"event=ci_costs.start table={path.name} runs={','.join(map(str, ids)) or 'default'} scan={scan}", flush=True)
    used, costs = collect(forge, ids, scan)
    if not costs:
        print("event=ci_costs.finish measured=0 table=unchanged: no run measured anything", file=sys.stderr)
        return 1
    measured = worst(costs)
    new, unmeasured, unplaced = merge(table, measured, used)
    changed = sum(1 for k in measured if k not in unplaced and lookup(table, k) != measured[k])
    if write:
        path.write_text(json.dumps(new, indent=1) + "\n")
    print(f"event=ci_costs.finish runs={','.join(map(str, used))} measured={len(measured)} changed={changed} "
          f"unmeasured={len(unmeasured)} unplaced={len(unplaced)} written={str(write).lower()}")
    if unmeasured:
        print(f"event=ci_costs.unmeasured kept={names(unmeasured)}")
    if unplaced:
        print(f"event=ci_costs.unplaced readings={names(unplaced)}")
    return 0


def lookup(table: dict[str, Any], key: Key) -> int | None:
    if key[0] == "ends":
        return table["ends"].get(key[1], {}).get(key[2])
    if key[0] == "rebased":
        return table["rebased"].get(key[1])
    steps = table["readings"].get(key[1], {}).get("steps_s", [])
    return steps[key[2]] if key[2] < len(steps) else None


def main(argv: list[str], gh: Gh = gh_cli) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="*", type=int)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--scan", type=int, default=40)
    ap.add_argument("--table", type=Path, default=TABLE)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    repo = a.repo or gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]).strip()
    return refresh(GitHub(repo, gh), a.runs, a.scan, a.table, not a.dry_run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
