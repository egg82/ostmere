"""Every backticked path in docs/systems.md and docs/engineering.md exists, and every backticked `module.symbol` in
docs/systems.md imports, so the inventory cannot describe code that is gone. Only code-shaped tokens are checked, never
the prose around them.

A reference to something not built yet is followed directly by `<!--planned-->`: it is skipped while its target is
missing and fails once the target exists (remove the marker then, so the reference is checked from then on). A
reference into another repository is followed by `<!--external-->` and is never checked. Do not drop the backticks to
get past this test."""
import importlib
import re
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
BASES = [ROOT, ROOT / "docs", ROOT / "app", ROOT / "app" / "ashfall_app"]
SKIP_DIRS = {"node_modules", ".git", "build", "build-dev"}
PATH = re.compile(r"^[~\w./*-]+\.(?:py|ts|mjs|md|txt|json|toml|ya?ml|sh|sql|html)$|^[\w.-]+(?:/[\w.-]+)+/$")
SYMBOL = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+$")
TOKEN = re.compile(r"`([^`\n]+)`(<!--(planned|external)-->)?")
# (document, floor on paths found, floor on symbols found, whether dotted names are symbols)
DOCS = [("docs/systems.md", 12, 1, True), ("docs/engineering.md", 18, 0, False)]


def path_exists(token: str) -> bool:
    """`token` (first word of a backticked span) resolves against the repo root, docs, app or the package; a bare file
    name is looked for anywhere in the tree."""
    if token.startswith("~"):
        return True  # outside this repo
    if "/" in token:
        return any(list(b.glob(token.rstrip("/"))) for b in BASES)
    return any(not SKIP_DIRS & set(p.parts) for p in ROOT.rglob(token))


def import_prefix(parts: list[str]) -> tuple[object, list[str]] | None:
    """The longest dotted prefix of `parts` that imports (as written, or under ashfall_app), with the rest."""
    for k in range(len(parts), 0, -1):
        for full in (".".join(parts[:k]), ".".join(["ashfall_app", *parts[:k]])):
            try:
                return importlib.import_module(full), parts[k:]
            except ImportError:
                continue
    return None


def symbol_exists(token: str) -> bool:
    """`module.symbol` (or `Name.attr` for a name the app's packages export) imports, down to a class field."""
    parts = token.split(".")
    found = import_prefix(parts)
    if found is None:
        homes = [importlib.import_module(n) for n in ("ashfall_app", "ashfall_app.engine", "ashfall_app.api", "ashfall_app.opening")]
        owner = next((m for m in homes if hasattr(m, parts[0])), None)
        found = (getattr(owner, parts[0]), parts[1:]) if owner is not None else None
    if found is None:
        return False
    obj, rest = found
    for attr in rest:
        known: set[str] = {f.name for f in fields(obj)} if is_dataclass(obj) else set()
        known |= set(getattr(obj, "__annotations__", {}))
        if not (hasattr(obj, attr) or attr in known):
            return False
        obj = getattr(obj, attr, None)
    return True


def check(
    text: str, symbols: bool, exists: Callable[[str], bool], imports: Callable[[str], bool]
) -> tuple[list[str], int, int]:
    """Problems in one document's text, plus how many paths and symbols it checked."""
    bad: list[str] = []
    paths = syms = 0
    for m in TOKEN.finditer(text):
        token, marker = m.group(1).split()[0] if m.group(1).strip() else "", m.group(3)
        if marker == "external":
            continue
        is_path = bool(PATH.match(token))
        if not is_path and not (symbols and SYMBOL.match(token)):
            continue
        ok = exists(token) if is_path else imports(token)
        paths, syms = paths + is_path, syms + (not is_path)
        if marker == "planned" and ok:
            bad.append(f"`{token}` is marked planned but exists now: remove the marker")
        elif marker != "planned" and not ok:
            bad.append(f"`{token}` does not resolve (mark it <!--planned--> if it is not built yet)")
    return bad, paths, syms


def test_the_citations_resolve():
    for doc, min_paths, min_syms, symbols in DOCS:
        bad, paths, syms = check((ROOT / doc).read_text(), symbols, path_exists, symbol_exists)
        assert not bad, f"{doc}:\n" + "\n".join(bad)
        assert paths >= min_paths and syms >= min_syms, f"{doc}: found {paths} paths, {syms} symbols: the scan is blind"


def test_the_checker_can_fail():
    """Controls: a missing path, a missing symbol and a bad marker each go red; a clean one and the markers stay quiet."""
    here = {"a/b.py": True, "ashfall_app.engine.Save.ended_at": True}

    def exists(token: str) -> bool:
        return here.get(token, False)

    imports = exists
    ok = "`a/b.py` and `ashfall_app.engine.Save.ended_at` and `plain` words"
    assert check(ok, True, exists, imports) == ([], 1, 1)
    assert len(check("`gone/x.py`", True, exists, imports)[0]) == 1
    assert len(check("`ashfall_app.engine.Save.nope`", True, exists, imports)[0]) == 1
    assert check("`gone/x.py`<!--planned-->", True, exists, imports)[0] == []
    assert len(check("`a/b.py`<!--planned-->", True, exists, imports)[0]) == 1
    assert check("`gone/x.py`<!--external-->", True, exists, imports)[0] == []
    assert check("`ashfall.yggdrasil.pub`", False, exists, imports) == ([], 0, 0)


def test_the_real_resolvers_can_fail():
    assert path_exists("docs/systems.md") and path_exists("DESIGN.txt") and path_exists("opening/renames.toml")
    assert not path_exists("docs/no-such-file.md") and not path_exists("no_such_file.py")
    assert symbol_exists("Save.ended_at") and symbol_exists("ashfall_app.engine.state.Save")
    assert not symbol_exists("Save.no_such_field") and not symbol_exists("NoSuchThing.x")
