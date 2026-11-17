"""Refresh the committed readouts from a CI run (docs/design/sim-invariants.md, "Readouts").

Run from app/: python -m tools.readouts_pull <run-id>

A job whose readout differs from its committed text fails after uploading the new text as a `readouts-new-*` artifact.
This downloads that run's artifacts and copies each readout into tests/readouts/; commit the result. A file whose name is
no readout's (a package's name, then `-` and a readout's name, then `.txt`) is refused.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.readout_snapshot import DIR, PACKAGES

NAME = re.compile(r"(?:%s)(?:-[a-z0-9_-]+)?\.txt" % "|".join(map(re.escape, PACKAGES)))


def accepted(name: str) -> bool:
    return NAME.fullmatch(name) is not None


def copy_in(source: Path, root: Path = DIR) -> tuple[list[Path], list[str]]:
    """(the files written under `root`, the names refused) from every file under `source`."""
    written: list[Path] = []
    refused: list[str] = []
    for f in sorted(p for p in source.rglob("*") if p.is_file() or p.is_symlink()):
        if f.is_symlink() or not accepted(f.name):
            refused.append(str(f.relative_to(source)))
            continue
        target = root / f.name
        shutil.copyfile(f, target)
        written.append(target)
    return written, refused


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not argv[0].isdigit():
        print(__doc__, file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["gh", "run", "download", argv[0], "-p", "readouts-new-*", "-D", tmp], check=True)
        written, refused = copy_in(Path(tmp))
    for f in written:
        print(f"wrote {f.relative_to(DIR.parent.parent)}")
    for name in refused:
        print(f"refused {name}: not a readout's name", file=sys.stderr)
    if not written and not refused:
        print("that run has no changed readouts", file=sys.stderr)
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
