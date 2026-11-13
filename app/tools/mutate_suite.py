"""Mutation run of a blind contract suite against the rows of its MUTANTS_<suite>.txt:
  held    tests/engine_contract/test_held_*.py    MUTANTS_held.txt    specs tools/held_mutants/
  drains  tests/engine_contract/test_drains_*.py  MUTANTS_drains.txt  specs tools/drains_mutants/
  spent   tests/engine_contract/test_spent_*.py   MUTANTS_spent.txt   specs tools/spent_mutants/
  heldspeed  tests/engine_contract/test_heldspeed_*.py  MUTANTS_heldspeed.txt  specs tools/heldspeed_mutants/
  leaves  tests/engine_contract/test_leaves_*.py  MUTANTS_leaves.txt  rows 1-20   specs tools/leaves_mutants/
  retire  tests/engine_contract/test_retire_*.py  MUTANTS_leaves.txt  rows 21-33  specs tools/retire_mutants/
  clocks  tests/db/test_failover.py (and the tests beside it in `also`)  tests/db/MUTANTS_clocks.txt  specs tools/clocks_mutants/
          the production code behind the tests that once waited on the wall clock; needs ASHFALL_TEST_PG
A suite may also run other test files beside its own (`also`: the implementation's tests, and the sibling suite sharing
its MUTANTS file); only its own tests make claims.

From app/:  python -m tools.mutate_suite SUITE --check
              exits 1 unless every row is claimed by a test marked @kills(row) and every claim names a row (a gate
              on the suite's own coverage; it plants nothing).
            python -m tools.mutate_suite SUITE --run [--only 1,5] [--specs DIR]
              copies app/ to a scratch directory, requires the unmutated suite to be green there with nothing
              skipped (a suite that skipped its database tests would let every mutant survive), then for each row
              applies DIR/mNN.py (default the suite's specs directory) and runs the suite.

A row may have variants, DIR/mNN.py and DIR/mNNx.py (one letter or more), each planted alone: the row passes when
every variant is KILLED, and one of the row's own claimed tests is red in some variant.
A spec is a module with EDITS, a list of (path under app/, old text, new text); each `old` must occur exactly once.
A spec may instead set EQUIVALENT to the reason no test can tell the mutant apart; it is then reported, never run.
A spec that moves every rules digest sets RELOCK = True: the session's release-lock fixture would refuse the shipped
content before any test ran, so the copy's lock is rewritten (content_lock.py --write) after planting, and the row's
own tests must then go red.
Outcomes, kept apart on purpose: KILLED (pytest exit 1 and a failing test), SURVIVED (exit 0), BROKEN (any other exit,
or a failure that is a collection or import error, which says the edit was malformed, not that a test noticed),
NOT PLANTED (no spec, or an anchor missing or not unique), EQUIVALENT. Only KILLED counts, and a row's @kills tests
must be among the ones that failed ("claim unmet" otherwise). Exit 1 unless every row run was KILLED with its claim met
or recorded EQUIVALENT.
"""
import argparse
import ast
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

APP = Path(__file__).resolve().parents[1]
CONTRACT = "tests/engine_contract"
ROW = re.compile(r"^ ?(\d+) \S")
"""A row starts in the first three columns (continuation lines are indented past them); its name fills columns 3-18."""
FAILED = re.compile(r"^FAILED (\S+)", re.M)


@dataclass(frozen=True)
class Suite:
    mutants: str
    tests: str
    specs: str
    first: int = 0
    last: int = 10**6
    also: tuple[str, ...] = ()
    """Globs under app/ of test files run with the suite's own, whose claims they do not make."""
    home: str = CONTRACT
    """The directory under app/ holding the suite's MUTANTS file and its own tests."""


SUITES = {
    "held": Suite("MUTANTS_held.txt", "test_held_*.py", "held_mutants"),
    "drains": Suite("MUTANTS_drains.txt", "test_drains_*.py", "drains_mutants"),
    "spent": Suite("MUTANTS_spent.txt", "test_spent_*.py", "spent_mutants"),
    "heldspeed": Suite("MUTANTS_heldspeed.txt", "test_heldspeed_*.py", "heldspeed_mutants"),
    "leaves": Suite("MUTANTS_leaves.txt", "test_leaves_*.py", "leaves_mutants", 1, 20, (
        "tests/engine_contract/test_retire_*.py", "tests/engine/test_leaves_impl.py",
        "tests/engine/test_retired_chores_impl.py", "tests/opening/test_leaves_loader.py",
        "tests/opening/test_retired_chores_loader.py")),
    "retire": Suite("MUTANTS_leaves.txt", "test_retire_*.py", "retire_mutants", 21, 33, (
        "tests/engine_contract/test_leaves_*.py", "tests/engine/test_leaves_impl.py",
        "tests/engine/test_retired_chores_impl.py", "tests/opening/test_leaves_loader.py",
        "tests/opening/test_retired_chores_loader.py")),
    "clocks": Suite("MUTANTS_clocks.txt", "test_failover.py", "clocks_mutants", also=(
        "tests/db/test_prune_race.py", "tests/db/test_reminders.py", "tests/reminders/test_sender.py",
        "tests/dayone/test_dayone_forecast.py"), home="tests/db"),
}


def rows(suite: Suite) -> dict[int, str]:
    lines = (APP / suite.home / suite.mutants).read_text().splitlines()
    found = {int(m[1]): line[3:19].strip() for line in lines if (m := ROW.match(line)) and suite.first <= int(m[1]) <= suite.last}
    if not found:
        sys.exit(f"{suite.mutants}: no rows parsed")
    return found


def claims(suite: Suite) -> dict[int, list[str]]:
    """Row -> the tests (file::name) marked @kills(row), read off the source, not by running anything. A claim of a row
    outside the suite's range is the sibling suite's."""
    out: dict[int, list[str]] = {}
    for path in sorted((APP / suite.home).glob(suite.tests)):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "kills":
                        for arg in dec.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, int) and suite.first <= arg.value <= suite.last:
                                out.setdefault(arg.value, []).append(f"{path.name}::{node.name}")
    return out


def check(suite: Suite) -> int:
    known, claimed = rows(suite), claims(suite)
    unclaimed = sorted(set(known) - set(claimed))
    unknown = sorted(set(claimed) - set(known))
    print(f"{len(known)} rows, {sum(len(v) for v in claimed.values())} claims")
    for n in unclaimed:
        print(f"row {n} ({known[n]}): no test claims it")
    for n in unknown:
        print(f"claim of row {n}: not a row of {suite.mutants}")
    return 1 if unclaimed or unknown else 0


@dataclass(frozen=True)
class Outcome:
    verdict: str
    failed: tuple[str, ...] = ()
    detail: str = ""


def scratch_copy(into: Path) -> Path:
    dest = into / "app"
    shutil.copytree(APP, dest, ignore=shutil.ignore_patterns("client", "__pycache__", ".pytest_cache", "node_modules",
                                                             ".hypothesis", "typings"))
    return dest


def pytest(app: Path, suite: Suite) -> tuple[int, str]:
    tests = sorted(str(p.relative_to(app)) for p in (app / suite.home).glob(suite.tests))
    assert tests, f"no {suite.tests} files to run"
    for pattern in suite.also:
        beside = sorted(str(p.relative_to(app)) for p in app.glob(pattern))
        assert beside, f"no {pattern} files to run"
        tests += beside
    env = {"PYTHONPATH": str(app), "PATH": "/usr/bin:/bin"}
    if pg := os.environ.get("ASHFALL_TEST_PG"):
        env["ASHFALL_TEST_PG"] = pg
    run = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-rf", *tests], cwd=app,
                         env=env, capture_output=True, text=True, check=False)
    return run.returncode, run.stdout + run.stderr


def load_spec(spec: Path) -> ModuleType:
    mod_spec = importlib.util.spec_from_file_location(spec.stem, spec)
    assert mod_spec is not None and mod_spec.loader is not None
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return mod


def plant(app: Path, edits: list[tuple[str, str, str]]) -> str | None:
    """Apply every edit, each anchor unique; None on success, else why not. The new text is read back."""
    for path, old, new in edits:
        target = app / path
        text = target.read_text()
        if text.count(old) != 1:
            return f"{path}: anchor occurs {text.count(old)} times"
        target.write_text(text.replace(old, new, 1))
        if new not in target.read_text():
            return f"{path}: the new text did not land"
    return None


def classify(code: int, out: str) -> Outcome:
    failed = tuple(FAILED.findall(out))
    if code == 0:
        return Outcome("SURVIVED")
    errors = [f for f in failed if "::" not in f] or re.findall(r"^ERROR (\S+)", out, re.M)
    if code != 1 or not failed or errors:
        return Outcome("BROKEN", failed, f"pytest exit {code}\n{out[-1500:]}")
    return Outcome("KILLED", failed)


def run_one(spec: Path, suite: Suite, base: Path) -> Outcome:
    mod = load_spec(spec)
    if hasattr(mod, "EQUIVALENT"):
        return Outcome("EQUIVALENT", detail=f"     {mod.EQUIVALENT}")
    with tempfile.TemporaryDirectory() as tmp:
        app = Path(tmp) / "app"
        shutil.copytree(base, app)
        why = plant(app, list(mod.EDITS))
        if why is not None:
            return Outcome("NOT PLANTED", detail=why)
        if getattr(mod, "RELOCK", False) and (why := relock(app)) is not None:
            return Outcome("BROKEN", detail=why)
        return classify(*pytest(app, suite))


def relock(app: Path) -> str | None:
    """Rewrite the copy's release lock for the planted engine; None on success, else why not."""
    run = subprocess.run([sys.executable, "tools/content_lock.py", "--write"], cwd=app,
                         env={"PYTHONPATH": str(app), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=False)
    return None if run.returncode == 0 else f"content_lock --write exit {run.returncode}\n{run.stdout[-800:]}{run.stderr[-800:]}"


def run(suite: Suite, only: set[int], specs: Path, failing: bool) -> int:
    known, claimed = rows(suite), claims(suite)
    with tempfile.TemporaryDirectory() as tmp:
        base = scratch_copy(Path(tmp))
        code, out = pytest(base, suite)
        if code != 0:
            print(f"the unmutated suite is not green (exit {code}); nothing to learn from a mutant\n{out[-2500:]}")
            return 1
        if skipped := re.findall(r"\d+ skipped", out):
            print(f"the unmutated suite skipped tests ({skipped[0]}): a skipped test cannot kill a mutant\n{out[-2500:]}")
            return 1
        print(f"baseline green: {re.findall(r'\d+ passed', out)}")
        bad = 0
        for n in sorted(only or set(known)):
            files = sorted([*specs.glob(f"m{n:02d}.py"), *specs.glob(f"m{n:02d}[a-z]*.py")])
            outs = [(f.stem, run_one(f, suite, base)) for f in files] or [(f"m{n:02d}", Outcome("NOT PLANTED", detail=f"no {specs}/m{n:02d}.py"))]
            mine = claimed.get(n, [])
            failed = {f for _, o in outs for f in o.failed}
            red = [t for t in mine if any(t.split("::")[1] in f for f in failed)]
            kinds = {o.verdict for _, o in outs}
            ok = kinds <= {"KILLED", "EQUIVALENT"} and (kinds == {"EQUIVALENT"} or not mine or bool(red))
            bad += not ok
            unmet = [t for t in mine if t not in red]
            print(f"{n:2d} {known[n]:<16} {', '.join(f'{name} {o.verdict} ({len(o.failed)} failing)' for name, o in outs)}"
                  + (f"; claimed but not red: {', '.join(unmet)}" if unmet and "KILLED" in kinds else "")
                  + ("; NO CLAIM MET" if kinds <= {"KILLED", "EQUIVALENT"} and "KILLED" in kinds and mine and not red else ""))
            for name, o in outs:
                if failing:
                    print("\n".join(f"     {name}: {f}" for f in o.failed))
                if o.detail:
                    print(o.detail)
        return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("suite", choices=sorted(SUITES))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--failing", action="store_true", help="with --run, list the failing tests of each mutant")
    ap.add_argument("--specs", type=Path, default=None)
    a = ap.parse_args()
    if a.check == a.run:
        ap.error("exactly one of --check, --run")
    suite = SUITES[a.suite]
    if a.check:
        return check(suite)
    specs = a.specs or APP / "tools" / suite.specs
    return run(suite, {int(x) for x in a.only.split(",") if x}, specs, a.failing)


if __name__ == "__main__":
    sys.exit(main())
