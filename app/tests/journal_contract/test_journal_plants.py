"""The journal contract's plants each apply to the composer exactly once (CI's `mutant-plants` runs the same command),
and the check names the plant whose anchor moved."""
import shutil
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parents[1]
CHECK = "tests/journal_contract/plant_mutants.py"
ANCHOR = "if any(line.at >= (day + 1) * DAY_S for line in lines):"


def _check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, CHECK, "--plants"], cwd=root, capture_output=True, text=True, timeout=60)


def _copy(tmp_path: Path, moved: bool) -> Path:
    """The composer and the plants in `tmp_path`; with `moved`, one plant's anchor edited out of the composer."""
    shutil.copytree(APP / "ashfall_app/saves", tmp_path / "ashfall_app/saves", ignore=shutil.ignore_patterns("__pycache__"))
    (tmp_path / "tests/journal_contract").mkdir(parents=True)
    for name in ("plant_mutants.py", "journal_plants.py"):
        shutil.copy(APP / "tests/journal_contract" / name, tmp_path / "tests/journal_contract" / name)
    if moved:
        day = tmp_path / "ashfall_app/saves/journal_composer/day.py"
        assert day.read_text().count(ANCHOR) == 1
        day.write_text(day.read_text().replace(ANCHOR, ANCHOR.replace(">=", ">")))
    return tmp_path


def test_every_journal_plant_applies_to_the_current_composer():
    done = _check(APP)
    assert done.returncode == 0, done.stdout
    assert "every one of" in done.stdout


def test_a_plant_whose_anchor_moved_fails_the_check_and_is_named(tmp_path: Path):
    done = _check(_copy(tmp_path, moved=True))
    assert done.returncode == 1
    assert "NOT PLANTED 8a: journal_composer/day.py: anchor found 0 times, not once" in done.stdout


def test_the_same_copy_without_the_edit_passes(tmp_path: Path):
    """The control for the test above: it is the edit that fails the check, not the copy."""
    assert _check(_copy(tmp_path, moved=False)).returncode == 0
