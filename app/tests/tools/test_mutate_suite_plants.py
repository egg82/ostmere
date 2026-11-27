"""The mutation tool names every spec that does not plant, before it runs anything."""
import sys
from pathlib import Path

import pytest

from tools import mutate_suite as ms

SPENT = ms.SUITES["spent"]
SPECS = ms.APP / "tools" / SPENT.specs


def _specs_with(tmp_path: Path, broken: str, old: str) -> Path:
    for f in SPECS.glob("m*.py"):
        (tmp_path / f.name).write_text(f.read_text())
    (tmp_path / broken).write_text(f'EDITS = [("ashfall_app/engine/mixes/spent.py", {old!r}, "pass\\n")]\n')
    return tmp_path


def test_every_spent_mutant_plants_on_the_current_engine():
    assert len(list(SPECS.glob("m*.py"))) >= len(ms.rows(SPENT))
    assert ms.unplanted(SPENT, SPECS) == []


def test_a_missing_anchor_is_reported_by_mutant_name(tmp_path: Path):
    specs = _specs_with(tmp_path, "m11.py", "text that is nowhere in the engine\n")
    assert ms.unplanted(SPENT, specs) == ["m11.py: ashfall_app/engine/mixes/spent.py: anchor occurs 0 times, not once"]


def test_an_anchor_that_occurs_twice_is_reported(tmp_path: Path):
    specs = _specs_with(tmp_path, "m11.py", "return ")
    (line,) = ms.unplanted(SPENT, specs)
    assert line.startswith("m11.py: ") and "times, not once" in line and "occurs 0 times" not in line


def test_a_row_with_no_spec_and_a_spec_with_no_row_are_reported(tmp_path: Path):
    specs = _specs_with(tmp_path, "m99.py", "def _in_play")
    (specs / "m11.py").unlink()
    assert sorted(ms.unplanted(SPENT, specs)) == [f"m11: no spec in {specs}", "m99.py: a spec for no row of MUTANTS_spent.txt"]


def test_a_run_stops_before_any_test_when_a_mutant_does_not_plant(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    specs = _specs_with(tmp_path, "m11.py", "text that is nowhere in the engine\n")
    assert ms.run(SPENT, set(), specs, False) == 1
    assert "NOT PLANTED m11.py" in capsys.readouterr().out


def test_plants_over_every_suite_exits_0_now_and_1_for_a_broken_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["mutate_suite", "--plants"])
    assert ms.main() == 0
    specs = _specs_with(tmp_path, "m11.py", "text that is nowhere in the engine\n")
    monkeypatch.setattr(sys, "argv", ["mutate_suite", "spent", "--plants", "--specs", str(specs)])
    assert ms.main() == 1
