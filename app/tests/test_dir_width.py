"""No directory holds more than LIMIT files directly: a directory of small files is grouped by subject into
subdirectories. Counts tracked files (`git ls-files`), so build output and ignored files never count. Directories
already over it are held in tests/held/dir_width.json as `{dir: {"files": n}}` through the shared ledger. A new wide
directory, or a held one that gained a file, fails; one that shrank fails as stale until the ledger is rewritten.
`python tests/test_dir_width.py --write` (from app/) rewrites the ledger; never run it to let a wider directory through."""
import subprocess
import sys
from pathlib import Path, PurePosixPath

from held_ledger import Ledger, dump, load, problems

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "app/tests/held/dir_width.json"
LIMIT = 20
WRITE = "python tests/test_dir_width.py --write"


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [p.decode() for p in out.split(b"\0") if p and (ROOT / p.decode()).is_file()]


def measure(paths: list[str]) -> Ledger:
    widths: dict[str, int] = {}
    for p in paths:
        d = PurePosixPath(p).parent.as_posix()
        widths[d] = widths.get(d, 0) + 1
    return {d: {"files": n} for d, n in widths.items() if n > LIMIT}


def counted() -> Ledger:
    return measure(tracked())


def test_the_gate_sees_the_tree():
    paths = tracked()
    assert len(paths) > 500 and "app/tests/test_dir_width.py" in paths, "the gate would pass on (nearly) nothing"


def test_the_held_ledger_is_what_the_tree_is():
    wrong = problems(
        counted(), load(HELD),
        f"over {LIMIT} files in one directory and not held: group them into subdirectories by subject", WRITE,
    )
    assert not wrong, "\n".join(wrong)


def test_planted_width_is_caught():
    """The measuring function goes red on a planted wide directory, and the ledger comparison on each way of drifting."""
    wide = [f"d/f{i}.py" for i in range(LIMIT + 1)]
    narrow = [f"e/f{i}.py" for i in range(LIMIT)]
    nested = [f"d/sub/f{i}.py" for i in range(LIMIT)]
    assert measure(narrow + nested) == {}
    assert measure(wide + narrow + nested) == {"d": {"files": LIMIT + 1}}
    held = {"d": {"files": LIMIT + 5}}
    assert problems(held, held, "", "") == []
    assert problems({"d": {"files": LIMIT + 6}}, held, "grew", "")[0].endswith("grew")
    assert "stale" in problems({"d": {"files": LIMIT + 4}}, held, "", "")[0]
    assert len(problems({"new": {"files": LIMIT + 1}}, held, "", "")) == 2


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        HELD.parent.mkdir(parents=True, exist_ok=True)
        HELD.write_text(dump(counted()))
        print(f"wrote {HELD.relative_to(ROOT)}: {len(counted())} directories held")
