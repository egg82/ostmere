"""No hand-written text file (`.md`, `.txt`, `.css`, and `.jsonl` under content/) passes LIMIT bytes: a document is a
group of subjects with an index, not one scroll. Files already over it are held in tests/held/text_size.json as
`{file: {"bytes": n}}` through the shared ledger. A new large file, or a held one that grew, fails; one that shrank
fails as stale until the ledger is rewritten. `python -m tests.gates.test_text_size --write` (from app/) rewrites the
ledger; never run it to let a larger file through.

Bytes, not lines: a prose or CSS line has no length bound, so a line count lets one file hide a megabyte. Generated
files, test fixtures and captured data are named in EXCLUDED, never recognised by their content."""
import subprocess
import sys
from pathlib import Path

from tests.held_ledger import Ledger, dump, load, problems, total

ROOT = Path(__file__).resolve().parent.parents[2]
HELD = ROOT / "app/tests/held/text_size.json"
LIMIT = 100_000
SUFFIXES = {".md", ".txt", ".css"}
EXCLUDED = ("app/client/generated/", "app/tests/fixtures/", "app/tests/readouts/")


def wanted(rel: str) -> bool:
    p = Path(rel)
    if rel.startswith(EXCLUDED):
        return False
    return p.suffix in SUFFIXES or (p.suffix == ".jsonl" and rel.startswith("content/"))


def files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return sorted(ROOT / r for r in out.decode().split("\0") if r and wanted(r) and (ROOT / r).is_file())


def measure(paths: list[Path], root: Path = ROOT) -> Ledger:
    out: Ledger = {}
    for p in paths:
        n = p.stat().st_size
        if n > LIMIT:
            out[p.relative_to(root).as_posix()] = {"bytes": n}
    return out


def counted() -> Ledger:
    return measure(files())


def test_the_gate_sees_the_text():
    names = {p.name for p in files()}
    assert len(names) > 100 and {"engineering.md", "game.css", "beat.jsonl"} <= names, "the gate would pass on (nearly) nothing"


def test_the_held_ledger_is_what_the_text_is():
    wrong = problems(
        counted(), load(HELD), f"over {LIMIT} bytes and not held: split it", "python -m tests.gates.test_text_size --write"
    )
    assert not wrong, "\n".join(wrong)


def test_what_is_wanted():
    assert wanted("docs/a.md") and wanted("x/y.css") and wanted("a.txt") and wanted("content/canon/beat.jsonl")
    assert not wanted("docs/research/x/notes.jsonl")
    assert not wanted("app/client/generated/openapi.json")
    assert not wanted("app/tests/fixtures/ci_health/runs.jsonl") and not wanted("app/tests/fixtures/ci_health/log.txt")


def test_a_planted_large_file_is_caught(tmp_path: Path):
    """The measuring function goes red on a planted file, and the ledger comparison on each way of drifting."""
    planted = tmp_path / "planted.md"
    planted.write_bytes(b"x" * (LIMIT + 1))
    small = tmp_path / "small.md"
    small.write_bytes(b"x" * LIMIT)
    assert measure([small], tmp_path) == {}
    assert measure([planted, small], tmp_path) == {"planted.md": {"bytes": LIMIT + 1}}
    held = {"a.md": {"bytes": LIMIT + 50}}
    assert problems(held, held, "", "") == []
    assert problems({"a.md": {"bytes": LIMIT + 51}}, held, "grew", "")[0].endswith("grew")
    assert "stale" in problems({"a.md": {"bytes": LIMIT + 1}}, held, "", "")[0]
    assert len(problems({"b.md": {"bytes": LIMIT + 50}}, held, "", "")) == 2


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        HELD.write_text(dump(counted()))
        print(f"wrote {HELD.relative_to(ROOT)}: {len(counted())} files, {total(counted())} bytes held")
