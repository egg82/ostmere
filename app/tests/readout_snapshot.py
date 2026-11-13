"""The pacing simulator's readouts, reported against their committed text (docs/design/sim-invariants.md). A readout
prints the rhythm of play, which is taste: it is read by a person and never fails a build. Its text is committed under
readouts/; when today's text differs, `check` reports the diff as a ReadoutChanged warning (pytest's warnings summary,
so the job's log shows it) and writes the new text under READOUTS_OUT for the job to keep. Only a readout that rendered
nothing fails: that is a broken play, not a change of taste. Writing the text again commits the new rhythm.

    python -m tests.readout_snapshot --write              # from app/: every package's readouts
    python -m tests.readout_snapshot --write dayone ...   # only the named packages

Each package's report module (PACKAGES) has NAMES, the readouts it owns, and `readouts() -> dict[str, str]`, which
plays what they need and renders them; its test_readouts.py renders the same text from the session's shared plays and
calls `check`. A package's readout names start with its own name."""
import difflib
import importlib
import os
import sys
import warnings
from pathlib import Path
from types import ModuleType

DIR = Path(__file__).resolve().parent / "readouts"
PACKAGES = {
    "opening": "tests.opening.report",
    "dayone": "tests.dayone.report",
    "daytwo": "tests.daytwo.report",
    "daythree": "tests.daythree.report",
    "weekone": "tests.weekone.report",
    "weektwo": "tests.weektwo.report",
    "ladder": "tests.ladder.readout",
    "worth": "tests.worth.readout",
}
OUT_ENV = "READOUTS_OUT"
"""Where a changed readout's new text is written for the CI job to keep as an artifact."""
SHOWN = 60
"""How many lines of a diff a report prints."""


class ReadoutChanged(UserWarning):
    """Today's readout differs from the committed text: a report for a person to read, never a failure."""


def path(name: str, root: Path = DIR) -> Path:
    return root / f"{name}.txt"


def differences(name: str, text: str, root: Path = DIR) -> list[str]:
    """The unified diff from the committed readout to `text`; every line of `text` when none is committed."""
    f = path(name, root)
    old = f.read_text().splitlines() if f.exists() else []
    return list(difflib.unified_diff(old, text.splitlines(), f"committed {name}", f"today's {name}", lineterm=""))


def check(name: str, text: str, root: Path = DIR) -> list[str]:
    """Report how `text` differs from the committed readout, and return the diff: a ReadoutChanged warning carrying the
    diff's first lines, and the new text written under OUT_ENV when it is set. Never fails on a difference, a readout
    with no committed text included. An empty readout fails: a play that rendered nothing is broken."""
    assert text.strip(), f"readout {name} rendered nothing"
    diff = differences(name, text, root)
    if not diff:
        return diff
    out = os.environ.get(OUT_ENV)
    if out:
        write(name, text, Path(out))
    more = f"\n... {len(diff) - SHOWN} more lines" if len(diff) > SHOWN else ""
    warnings.warn(ReadoutChanged(f"readout {name} changed (to commit it: python -m tests.readout_snapshot --write "
                                 f"{name.split('-')[0]})\n" + "\n".join(diff[:SHOWN]) + more), stacklevel=2)
    return diff


def write(name: str, text: str, root: Path = DIR) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    f = path(name, root)
    f.write_text(text if text.endswith("\n") else text + "\n")
    return f


def stray(package: str, names: tuple[str, ...], root: Path = DIR) -> tuple[list[str], list[str]]:
    """(committed files of `package` no readout writes, readouts of `package` with no committed file)."""
    have = {f.stem for f in root.glob("*.txt") if f.stem == package or f.stem.startswith(package + "-")}
    return sorted(have - set(names)), sorted(set(names) - have)


def module(package: str) -> ModuleType:
    return importlib.import_module(PACKAGES[package])


def write_package(package: str, root: Path = DIR) -> list[Path]:
    """Every readout of `package`, written; committed files it no longer writes are removed."""
    m = module(package)
    texts: dict[str, str] = m.readouts()
    assert set(texts) == set(m.NAMES), (sorted(texts), m.NAMES)
    for gone in stray(package, tuple(texts), root)[0]:
        path(gone, root).unlink()
    return [write(name, text, root) for name, text in sorted(texts.items())]


def main(argv: list[str]) -> int:
    if not argv or argv[0] != "--write" or any(a not in PACKAGES for a in argv[1:]):
        print(__doc__, file=sys.stderr)
        return 2
    for package in argv[1:] or PACKAGES:
        for f in write_package(package):
            print(f"wrote {f.relative_to(DIR.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
