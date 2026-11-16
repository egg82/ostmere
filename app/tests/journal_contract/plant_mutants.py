"""Plants each wrong implementation in journal_plants.py (MUTANTS.txt's rows) in a copy of the app tree, never the tree
itself, and runs that row's bracketed test modules against it (the whole contract suite for the equivalents).

A kill is pytest exit 1 with a FAILED line and, among the failures, an assertion, a DID NOT RAISE or a timeout; failures
made only of other exceptions are the plant's own breakage (`broken`), and a plant whose old text is not found exactly
once is `unplanted`. A survivor of the push profile runs again at HYPOTHESIS_PROFILE=ci, then against the whole suite.
The unmutated copy must pass first, and each mutated file is restored byte for byte before the next plant.

From app/: `python tests/journal_contract/plant_mutants.py [id ...]` (no ids: every plant), or `... --plants`: plants
nothing and runs no test, and exits 1 naming each plant whose anchor is not found exactly once (CI, `mutant-plants`)."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from journal_plants import PLANTS, Edit

HERE = Path(__file__).resolve().parent
APP = HERE.parents[1]
SUITE = "tests/journal_contract"
KILLING = ("AssertionError", "assert ", "DID NOT RAISE", "Timeout")


@dataclass(frozen=True)
class Outcome:
    status: str
    profile: str
    detail: str


def bracketed() -> dict[str, list[str]]:
    """MUTANTS.txt's row number to the test modules its brackets name."""
    text = (HERE / "MUTANTS.txt").read_text().split("Equivalent (")[0]
    rows: dict[str, list[str]] = {}
    for chunk in re.split(r"\n(?=\s?\d+ )", text):
        found = re.match(r"\s?(\d+) ", chunk)
        names = re.findall(r"\[([a-z_, ]+)\]", chunk)
        if found and names:
            rows[found.group(1)] = [f"{SUITE}/test_journal_{n.strip()}.py" for n in names[-1].split(",")]
    return rows


def pytest(root: Path, paths: list[str], profile: str) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "HYPOTHESIS_PROFILE": profile}
    args = [sys.executable, "-m", "pytest", *paths, "-q", "-p", "no:cacheprovider", "--tb=line"]
    try:
        done = subprocess.run(args, cwd=root, env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return -1, "the run timed out"
    return done.returncode, done.stdout + done.stderr


def judge(code: int, out: str, profile: str) -> Outcome:
    failed = re.findall(r"^FAILED (\S+)", out, re.M)
    if code == -1:
        return Outcome("killed", profile, "timeout")
    if code == 0:
        return Outcome("survived", profile, "")
    if code == 1 and failed and any(k in out for k in KILLING):
        return Outcome("killed", profile, failed[0])
    errors = sorted(set(re.findall(r"^\S+:\d+: (\w+Error)", out, re.M)))
    return Outcome("broken", profile, f"exit {code}: {', '.join(errors) or out.strip().splitlines()[-1:]}")


def planted(saves: Path, edits: list[Edit]) -> tuple[dict[Path, str], dict[Path, str]] | str:
    """The edits applied in memory: (each touched file's original text, its planted text), or what is wrong with the
    first edit that does not apply (an anchor not found exactly once, or an edit that changes nothing)."""
    originals: dict[Path, str] = {}
    texts: dict[Path, str] = {}
    for name, old, new in edits:
        path = saves / name
        originals.setdefault(path, path.read_text())
        text = texts.get(path, originals[path])
        if text.count(old) != 1:
            return f"{name}: anchor found {text.count(old)} times, not once"
        if old == new:
            return f"{name}: the edit changes nothing"
        texts[path] = text.replace(old, new, 1)
    return originals, texts


def unplanted(saves: Path) -> list[str]:
    """Each plant that does not apply to the code in `saves`, with why."""
    out: list[str] = []
    for pid, edits in PLANTS.items():
        result = planted(saves, edits)
        if isinstance(result, str):
            out.append(f"{pid}: {result}")
    return out


def plant(saves: Path, edits: list[Edit]) -> dict[Path, str] | None:
    """Applies the edits, returning each touched file's original text; None (nothing written) when one does not apply."""
    result = planted(saves, edits)
    if isinstance(result, str):
        return None
    originals, texts = result
    for path, text in texts.items():
        path.write_text(text)
        assert path.read_text() == text != originals[path], path
    return originals


def restore(originals: dict[Path, str]) -> None:
    for path, text in originals.items():
        path.write_text(text)
        assert path.read_text() == text, path


def run_one(root: Path, pid: str, modules: list[str]) -> Outcome:
    originals = plant(root / "ashfall_app/saves", PLANTS[pid])
    if originals is None:
        return Outcome("unplanted", "", "an anchor is not found exactly once")
    try:
        outcome = judge(*pytest(root, modules, "contract"), "contract")
        if outcome.status == "survived":
            outcome = judge(*pytest(root, modules, "ci"), "ci")
        if outcome.status == "survived" and modules != [SUITE]:
            whole = judge(*pytest(root, [SUITE], "ci"), "ci, whole suite")
            outcome = whole if whole.status != "survived" else outcome
        return outcome
    finally:
        restore(originals)


def copy_tree(dest: Path) -> Path:
    root = dest / "app"
    skip = shutil.ignore_patterns("__pycache__", ".hypothesis", "node_modules")
    for part in ("ashfall_app", "tests"):
        shutil.copytree(APP / part, root / part, ignore=skip)
    shutil.copy(APP / "pytest.ini", root / "pytest.ini")
    return root


def main(ids: list[str]) -> int:
    rows = bracketed()
    with tempfile.TemporaryDirectory(prefix="journal-mutants-") as tmp:
        root = copy_tree(Path(tmp))
        code, out = pytest(root, [SUITE], "contract")
        if code != 0:
            print(out[-3000:])
            print("the unmutated copy is not green: nothing to measure")
            return 2
        results = {pid: run_one(root, pid, rows.get(pid.rstrip("abcdefghij"), [SUITE])) for pid in ids or list(PLANTS)}
    for pid, o in results.items():
        print(f"{pid:>4} {o.status:<9} {o.profile:<16} {o.detail}")
    mutants = {p: o for p, o in results.items() if not p.startswith("E")}
    killed = sum(o.status == "killed" for o in mutants.values())
    missed = sorted(p for p, o in mutants.items() if o.status != "killed")
    print(f"killed {killed}/{len(mutants)}; not killed: {missed}")
    return 0


def check_plants() -> int:
    bad = unplanted(APP / "ashfall_app/saves")
    print("\n".join(f"NOT PLANTED {line}" for line in bad) or f"every one of {len(PLANTS)} plants applies exactly once")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(check_plants() if sys.argv[1:] == ["--plants"] else main(sys.argv[1:]))
