"""The paths a playthrough-marked test depends on (docs/engineering.md, "Structural gates").

Run from app/: python -m tools.playthrough_paths --write   rewrites playthrough_paths.txt (repo-root-relative)
               python -m tools.playthrough_paths --match F...  prints the files among F... the list covers (CI's `changes` job)
CI reads the committed list, so a change to any listed path runs the playthroughs without an import walk there.

A path is listed when it is a Python module the playthrough tests import (transitively, inside ashfall_app and tests),
a conftest above them, a data file beside any such module, or under content/ (read by the play tests). A line ending
in `/` is a prefix.
"""
import ast
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
ROOT = APP.parent
LISTING = Path(__file__).with_name("playthrough_paths.txt")
PACKAGES = ("ashfall_app", "tests")
CONFIG = ("app/pytest.ini", "app/requirements.txt")
PREFIXES = ("content/",)


def playthrough_tests() -> list[Path]:
    """The test files that mark anything `playthrough` (a decorator or a `pytestmark`), found without collecting."""
    files = [f for f in sorted((APP / "tests").rglob("test_*.py"))
             if any(isinstance(n, ast.Attribute) and n.attr == "playthrough"
                    for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))))]
    if not files:
        sys.exit("no test file marks a playthrough: the walk found nothing to start from")
    return files


def module_file(dotted: str) -> Path | None:
    base = APP.joinpath(*dotted.split("."))
    for found in (base.with_suffix(".py"), base / "__init__.py"):
        if found.is_file():
            return found
    return None


def imports(path: Path) -> set[Path]:
    """The in-repo modules `path` imports (every import statement, lazy ones too), with their package `__init__`s."""
    parts = path.relative_to(APP).with_suffix("").parts
    package = list(parts if path.name == "__init__.py" else parts[:-1])
    if path.name == "__init__.py":
        package = list(parts[:-1])
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            base = ".".join(package[:len(package) - node.level + 1]) if node.level else ""
            mod = ".".join(x for x in (base, node.module or "") if x)
            names.add(mod)
            names |= {f"{mod}.{a.name}" for a in node.names}
    found: set[Path] = set()
    for name in names:
        if name.split(".")[0] not in PACKAGES:
            continue
        pieces = name.split(".")
        for i in range(1, len(pieces) + 1):
            if (m := module_file(".".join(pieces[:i]))) is not None:
                found.add(m)
    return found


def computed() -> list[str]:
    todo = list(playthrough_tests())
    for test in list(todo):
        parent = test.parent
        while parent != APP.parent:
            todo += [c for c in (parent / "conftest.py",) if c.is_file()]
            parent = parent.parent
    seen: set[Path] = set()
    while todo:
        path = todo.pop()
        if path not in seen:
            seen.add(path)
            todo += sorted(imports(path))
    data = {f for d in {p.parent for p in seen} for f in d.iterdir()
            if f.is_file() and f.suffix not in (".py", ".pyc")}
    return sorted({str(p.relative_to(ROOT)) for p in seen | data} | set(CONFIG) | set(PREFIXES))


def covers(listing: list[str], path: str) -> bool:
    return any(path == line or (line.endswith("/") and path.startswith(line)) for line in listing)


def committed() -> list[str]:
    return LISTING.read_text(encoding="utf-8").split()


def main(argv: list[str]) -> int:
    if argv[:1] == ["--write"]:
        LISTING.write_text("\n".join(computed()) + "\n", encoding="utf-8")
        return 0
    if argv[:1] == ["--match"]:
        listing = committed()
        print("\n".join(f for f in argv[1:] if covers(listing, f)))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
