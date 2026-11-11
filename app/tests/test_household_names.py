"""No file in the repository names the household that runs it: its people, pets, network, towns or hosts. The names are
never in the tree, in any form: CI supplies them in `OSTMERE_HOUSEHOLD_NAMES` (one per line or comma-separated, a CI
secret), and without it the scan skips. Every word, every dotted or hyphenated compound (`host.example.home`,
`10.0.0.1`, `ws-name01`) and every pair of adjacent words of each tracked text file is looked up, lower-cased.

A file may keep a name only under `KEPT`, a held ledger of per-file counts that may only shrink: a word the game uses
for its own sake that happens to be a held name too. CI's output gives paths and counts, never the names."""

import os
import re
import subprocess
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
CANARY = "zq-household-canary"  # always held, so the scan is proven able to find a name
COMPOUND = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)+")
WORD = re.compile(r"[a-z0-9]+")

# Per-file counts of held names a file may still carry; may only go down.
KEPT: dict[str, int] = {
    "app/tests/test_household_names.py": 1,
}


def held() -> frozenset[str]:
    """The names CI supplies, lower-cased, plus the canary; just the canary when none are supplied."""
    given = re.split(r"[\n,]", os.environ.get("OSTMERE_HOUSEHOLD_NAMES", ""))
    return frozenset({n.strip().lower() for n in given if n.strip()} | {CANARY})


def tokens(text: str) -> Iterable[str]:
    lowered = text.lower()
    words = WORD.findall(lowered)
    yield from words
    yield from COMPOUND.findall(lowered)
    yield from (f"{a} {b}" for a, b in zip(words, words[1:]))


def hits(text: str, names: frozenset[str]) -> int:
    return sum(1 for t in tokens(text) if t in names)


SKIPPED_DIRS = frozenset({".git", "node_modules", "build", "dist", "__pycache__", ".venv", ".pytest_cache",
                          ".hypothesis"})


def tracked() -> list[Path]:
    """The tracked files, by `git ls-files`; where there is no git, every file outside `SKIPPED_DIRS`."""
    try:
        listed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return walked()
    return [ROOT / p for p in listed.decode().split("\0") if p]


def walked() -> list[Path]:
    found: list[Path] = []
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        found += [Path(directory) / f for f in files]
    return found


@pytest.fixture(scope="module")
def found() -> tuple[int, Counter[str]]:
    names = held()
    if names == frozenset({CANARY}):
        pytest.skip("OSTMERE_HOUSEHOLD_NAMES is unset: CI supplies the household's names as a secret")
    counts: Counter[str] = Counter()
    scanned = 0
    for path in tracked():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        scanned += 1
        n = hits(text, names)
        if n:
            counts[str(path.relative_to(ROOT))] = n
    return scanned, counts


def test_no_file_names_the_household(found: tuple[int, Counter[str]]) -> None:
    scanned, counts = found
    assert scanned > 1000, f"scanned only {scanned} files"
    over = {p: n for p, n in counts.items() if n > KEPT.get(p, 0)}
    assert over == {}, "a household name (people, pet, network, town, host): move it to settings or reword it"


def test_the_kept_ledger_equals_the_tree(found: tuple[int, Counter[str]]) -> None:
    _, counts = found
    stale = {p: (n, counts.get(p, 0)) for p, n in KEPT.items() if counts.get(p, 0) < n}
    assert stale == {}, "stale: lower or remove these KEPT entries (held, found)"


def test_the_scan_finds_a_held_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSTMERE_HOUSEHOLD_NAMES", "Robin Doe, ws-robin01\nexample.home")
    names = held()
    assert names == frozenset({"robin doe", "ws-robin01", "example.home", CANARY})
    assert hits(f"see {CANARY} and Robin Doe on ws-robin01 at example.home", names) == 4
    assert hits("a household of Toby and Sam at ha.test", names) == 0
