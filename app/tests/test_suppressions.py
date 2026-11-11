"""Every suppression is counted per file in tests/held/suppressions.json and the counts only go down: `# pyright: ignore`,
`# type: ignore`, `# noqa`, `typing.cast(` and, in the client, `@ts-ignore`, `@ts-expect-error` and `as unknown as` each
remove an error the way a fix does, and a count cannot tell the two apart.

A suppression names its rule (`pyright: ignore[rule]`, `noqa: CODE`, `type: ignore[code]`) and carries a reason on the
same line after ` -- ` (`# noqa: E402 -- sys.path is set above`). One that lacks either is counted under `unexplained`,
which is held too: fix it by writing the reason, never by raising the count. Never cast a value to quiet a safety type.
`python tests/test_suppressions.py --write` (from app/) rewrites the ledger; never run it to let a suppression through."""
import ast
import io
import re
import sys
import tokenize
from functools import cache
from pathlib import Path

from held_ledger import Ledger, dump, load, problems, tally, total

ROOT = Path(__file__).resolve().parents[2]
PY_SRC = [ROOT / "app/ashfall_app", ROOT / "app/tests", ROOT / "app/tools", ROOT / "tools"]
TS_SRC = [ROOT / "app/client/src", ROOT / "app/client/test"]
HELD = ROOT / "app/tests/held/suppressions.json"
REASON = re.compile(r"\s--\s+\S.{2,}")
PY_COMMENT = [
    ("pyright-ignore", re.compile(r"#\s*pyright:\s*ignore(\[[^\]]+\])?"), True),
    ("type-ignore", re.compile(r"#\s*type:\s*ignore(\[[^\]]+\])?"), True),
    ("noqa", re.compile(r"#\s*noqa(:\s*[A-Z]+\d+)?"), True),
]
TS_LINE = [
    ("ts-ignore", re.compile(r"@ts-ignore")),
    ("ts-expect-error", re.compile(r"@ts-expect-error")),
    ("as-unknown-as", re.compile(r"\bas unknown as\b")),
]


def py_suppressions(source: str) -> list[tuple[str, bool]]:
    """(kind, explained) per Python suppression: comments by the tokenizer, `cast(` calls by the parser, so a string
    that mentions one is not counted."""
    out: list[tuple[str, bool]] = []
    if not ("ignore" in source or "noqa" in source or "cast" in source):
        return out  # nothing to find: skip the tokenizer and the parser
    lines = source.splitlines()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type != tokenize.COMMENT:
            continue
        for kind, pat, needs_rule in PY_COMMENT:
            m = pat.search(tok.string)
            if m:
                named = bool(m.group(1)) or not needs_rule
                out.append((kind, named and bool(REASON.search(lines[tok.start[0] - 1]))))
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            f = node.func
            if (isinstance(f, ast.Name) and f.id == "cast") or (isinstance(f, ast.Attribute) and f.attr == "cast"):
                out.append(("cast", bool(REASON.search(lines[node.lineno - 1]))))
    return out


def ts_suppressions(source: str) -> list[tuple[str, bool]]:
    return [
        (kind, bool(REASON.search(line)))
        for line in source.splitlines()
        for kind, pat in TS_LINE
        if pat.search(line)
    ]


def ledger(found: dict[str, list[tuple[str, bool]]]) -> Ledger:
    items = [(f, k) for f, ks in found.items() for k, _ in ks]
    items += [(f, "unexplained") for f, ks in found.items() for _, ok in ks if not ok]
    return tally(items)


@cache
def scan() -> dict[str, list[tuple[str, bool]]]:
    out: dict[str, list[tuple[str, bool]]] = {}
    for dirs, suffix, fn in ((PY_SRC, ".py", py_suppressions), (TS_SRC, ".ts", ts_suppressions)):
        for p in sorted(p for d in dirs for p in d.rglob("*") if p.suffix == suffix and "node_modules" not in p.parts):
            found = fn(p.read_text(encoding="utf-8"))
            if found:
                out[p.relative_to(ROOT).as_posix()] = found
    return out


def test_the_gate_sees_the_code():
    found = scan()
    kinds = {k for ks in found.values() for k, _ in ks}
    assert {"cast", "noqa", "as-unknown-as"} <= kinds, f"the scan found only {sorted(kinds)}: it would pass on nothing"


def test_the_held_ledger_is_what_the_code_is():
    wrong = problems(
        ledger(scan()), load(HELD),
        "a suppression added, or one without its rule and ` -- reason`: fix the cause or explain it",
        "python tests/test_suppressions.py --write",
    )
    assert not wrong, "\n".join(wrong)


def test_planted_suppressions_are_counted_and_explained_ones_told_apart():
    py = (
        "import typing\n"
        "a = typing.cast(int, 1)\n"
        "b = cast(int, 1)  # sound -- json narrowed above\n"
        "c = f(x)  # pyright: ignore[reportFoo] -- stubs are partial\n"
        "d = f(x)  # pyright: ignore\n"
        "e = f(x)  # type: ignore[arg-type]\n"
        "from y import z  # noqa: E402 -- path set above\n"
        "from y import w  # noqa\n"
        's = "# noqa and cast(int, 1) in a string"\n'
    )
    assert py_suppressions(py) == [
        ("pyright-ignore", True), ("pyright-ignore", False), ("type-ignore", False),
        ("noqa", True), ("noqa", False), ("cast", False), ("cast", True),
    ]
    ts = "const a = x as unknown as Y;\nconst b = x as unknown as Y; // fake node -- the test double\n// @ts-ignore\n"
    assert ts_suppressions(ts) == [("as-unknown-as", False), ("as-unknown-as", True), ("ts-ignore", False)]
    assert ledger({"a.py": [("cast", False), ("cast", True)]}) == {"a.py": {"cast": 2, "unexplained": 1}}
    held = {"a.py": {"cast": 1}}
    assert problems(held, held, "", "") == []
    assert problems({"a.py": {"cast": 2}}, held, "added", "")[0].endswith("added")
    assert "stale" in problems({}, held, "", "")[0]


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        HELD.parent.mkdir(parents=True, exist_ok=True)
        led = ledger(scan())
        HELD.write_text(dump(led))
        print(f"wrote {HELD.relative_to(ROOT)}: {len(led)} files, {total(led)} counts held")
