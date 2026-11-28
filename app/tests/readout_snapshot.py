"""The pacing simulator's readouts, reported against their committed text (docs/design/sim-invariants.md). A readout
prints the rhythm of play, which is taste: what it says is never judged against a threshold. Its text is committed under
readouts/<group> (`group`); when today's text differs, `check` reports the diff as a ReadoutChanged warning (pytest's
warnings summary, so the job's log shows it) and writes the new text under READOUTS_OUT, which the job uploads and then
fails on: a committed text that differs from what the code renders is stale. A readout that rendered nothing fails too.
Refresh with
`python -m tools.readouts_pull <run-id>` from app/, or write the text again locally to commit the new rhythm.

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
    "opening": "tests.rules.play.report",
    "tracks": "tests.rules.play.tracks_readout",
    "town": "tests.rules.play.town_readout",
    "closecalls": "tests.rules.play.close_calls_readout",
    "pronouns": "tests.rules.play.pronouns_readout",
    "dayone": "tests.dayone.pacing.report",
    "daytwo": "tests.daytwo.report",
    "daythree": "tests.daythree.report",
    "weekone": "tests.weekone.report",
    "weektwo": "tests.weektwo.report",
    "ladder": "tests.ladder.readout",
    "makers": "tests.makers.readout",
    "worth": "tests.worth.readout",
}
GROUPS = {"opening": "rules", "tracks": "rules", "town": "rules", "closecalls": "rules", "pronouns": "rules"}
"""The subdirectory of readouts/ a package's files live in: its own name unless listed here."""
OUT_ENV = "READOUTS_OUT"
"""Where a changed readout's new text is written for the CI job to keep as an artifact."""
SHOWN = 60
"""How many lines of a diff a report prints."""


class ReadoutChanged(UserWarning):
    """Today's readout differs from the committed text: the test warns; the job fails after uploading it."""


def group(name: str) -> str:
    """The subdirectory of readouts/ holding readout `name` (a package's name, or its name then `-` and more)."""
    package = name.split("-")[0]
    return GROUPS.get(package, package)


def path(name: str, root: Path = DIR) -> Path:
    return root / group(name) / f"{name}.txt"


def differences(name: str, text: str, root: Path = DIR) -> list[str]:
    """The unified diff from the committed readout to `text`; every line of `text` when none is committed."""
    f = path(name, root)
    old = f.read_text().splitlines() if f.exists() else []
    return list(difflib.unified_diff(old, text.splitlines(), f"committed {name}", f"today's {name}", lineterm=""))


def check(name: str, text: str, root: Path = DIR) -> list[str]:
    """Report how `text` differs from the committed readout, and return the diff: a ReadoutChanged warning carrying the
    diff's first lines, and the new text written under OUT_ENV when it is set. The test never fails on a difference
    (the job does, after the upload), a readout with no committed text included. An empty readout fails: a broken play."""
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
    f = path(name, root)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text if text.endswith("\n") else text + "\n")
    return f


def stray(package: str, names: tuple[str, ...], root: Path = DIR) -> tuple[list[str], list[str]]:
    """(committed files of `package` no readout writes, readouts of `package` with no committed file)."""
    have = {f.stem for f in (root / group(package)).glob("*.txt") if f.stem == package or f.stem.startswith(package + "-")}
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
