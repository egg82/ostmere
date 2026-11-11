"""No source file grows past LIMIT lines: a file is a group of functions with one purpose, not a feature's worth of
everything. Files already over it are held in tests/held/file_size.json as `{file: {"lines": n}}` through the shared
ledger. A new long file, or a held one that grew, fails; one that shrank fails as stale until the ledger is rewritten.
`python tests/test_file_size.py --write` (from app/) rewrites the ledger; never run it to let a longer file through."""
import sys
from pathlib import Path

from held_ledger import Ledger, dump, load, problems, total

ROOT = Path(__file__).resolve().parents[2]
SRC = [ROOT / "app/ashfall_app", ROOT / "app/tools", ROOT / "tools", ROOT / "app/client/src"]
SUFFIXES = {".py", ".ts"}
HELD = ROOT / "app/tests/held/file_size.json"
LIMIT = 300


def files() -> list[Path]:
    return sorted(
        p for d in SRC for p in d.rglob("*")
        if p.suffix in SUFFIXES and p.is_file() and "node_modules" not in p.parts
    )


def measure(paths: list[Path]) -> Ledger:
    out: Ledger = {}
    for p in paths:
        n = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
        if n > LIMIT:
            out[p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.name] = {"lines": n}
    return out


def counted() -> Ledger:
    return measure(files())


def test_the_gate_sees_the_code():
    names = {p.name for p in files()}
    assert len(names) > 50 and {"main.py", "main.ts"} <= names, "the gate would pass on (nearly) nothing"


def test_the_held_ledger_is_what_the_code_is():
    wrong = problems(
        counted(), load(HELD), f"over {LIMIT} lines and not held: split it", "python tests/test_file_size.py --write"
    )
    assert not wrong, "\n".join(wrong)


def test_a_planted_long_file_is_caught(tmp_path: Path):
    """The measuring function goes red on a planted file, and the ledger comparison on each way of drifting."""
    planted = tmp_path / "planted.py"
    planted.write_text("x = 1\n" * (LIMIT + 1))
    short = tmp_path / "short.py"
    short.write_text("x = 1\n" * LIMIT)
    assert measure([short]) == {}
    assert measure([planted, short]) == {"planted.py": {"lines": LIMIT + 1}}
    held = {"a.py": {"lines": LIMIT + 50}}
    assert problems(held, held, "", "") == []
    assert problems({"a.py": {"lines": LIMIT + 51}}, held, "grew", "")[0].endswith("grew")
    assert "stale" in problems({"a.py": {"lines": LIMIT + 1}}, held, "", "")[0]
    assert len(problems({"b.py": {"lines": LIMIT + 50}}, held, "", "")) == 2


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        HELD.parent.mkdir(parents=True, exist_ok=True)
        HELD.write_text(dump(counted()))
        print(f"wrote {HELD.relative_to(ROOT)}: {len(counted())} files, {total(counted())} lines held")
