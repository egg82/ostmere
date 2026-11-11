"""flatcheck.py reads every chapter list: the shipped week-1 order raises nothing but recorded acceptances, and each
planted chapter entry is flagged (in a fixture copy of beats.yaml, never the shipped file)."""
import subprocess
import sys
from pathlib import Path

import pytest

from tests.dayone.beats import BEATS_YAML
from tests.dayone.story import FLATCHECK

SHIPPED = BEATS_YAML.read_text()
L3_TURN = "turn: up, cost: none, advances: [C-promise-20], moves: [N1, PC]"
G2_PAYS = 'cost: none, pays: [C-promise-22], moves: [PC, N1]'
PLANTS = {
    "turn_run3": (L3_TURN, L3_TURN.replace("turn: up", "turn: down")),
    "near_unpaid": (G2_PAYS, G2_PAYS.replace("pays: [C-promise-22], ", "")),
}


def run(text: str, tmp: Path, *extra: str) -> tuple[int, list[tuple[str, str]]]:
    """The exit status and each flag as (the beat it names, the flag)."""
    f = tmp / "beats.yaml"
    f.write_text(text)
    out = subprocess.run([sys.executable, str(FLATCHECK), str(f), *extra], capture_output=True, text=True, check=False)
    return out.returncode, [(ln.split()[0], ln.split()[1]) for ln in out.stdout.splitlines()
                            if ln.split()[1:2] and "=" not in ln.split()[0]]


def test_the_shipped_chapters_raise_nothing_but_recorded_acceptances(tmp_path: Path):
    code, flags = run(SHIPPED, tmp_path, "--decisions", str(BEATS_YAML.parent / "decisions.jsonl"))
    assert code == 0 and flags  # the acceptances print, so the run examined them


@pytest.mark.parametrize("flag", sorted(PLANTS))
def test_each_planted_chapter_entry_is_flagged(flag: str, tmp_path: Path):
    """The plant raises its flag at a beat the unplanted file raises it at nowhere, so the flag is the plant's."""
    old, new = PLANTS[flag]
    assert SHIPPED.count(old) == 1
    code, flags = run(SHIPPED.replace(old, new), tmp_path, "--decisions", str(tmp_path / "none"))
    _, base = run(SHIPPED, tmp_path, "--decisions", str(tmp_path / "none"))
    assert code != 0 and [f for f in flags if f[1] == flag and f not in base]
