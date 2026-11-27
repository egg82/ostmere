"""The engine's design text is a directory of parts, `engine/design/`, listed in order by `engine/DESIGN.txt`: every part
is listed once and every listed part exists, and every `design/<part>.txt` cited in the repo's text is a part."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "app/ashfall_app/engine"
LISTED = re.compile(r"^design/([\w-]+\.txt):", re.M)
CITED = re.compile(r"(?<![\w-])design/([\w-]+\.txt)")
SKIP_SUFFIXES = {".png", ".jpg", ".svg", ".woff2", ".ogg", ".mp3", ".wav", ".gz", ".zip", ".webp", ".ico"}


def index_problems(listed: list[str], present: set[str]) -> list[str]:
    out = [f"{n} is listed twice" for n in sorted({n for n in listed if listed.count(n) > 1})]
    out += [f"{n} is listed but missing" for n in sorted(set(listed) - present)]
    out += [f"{n} is not listed" for n in sorted(present - set(listed))]
    return out


def cited_problems(text: str, present: set[str]) -> list[str]:
    return [f"cites design/{n}, which is not a part" for n in CITED.findall(text) if n not in present]


def present_parts() -> set[str]:
    return {p.name for p in (ENGINE / "design").glob("*.txt")}


def test_the_index_lists_every_part_once():
    listed = LISTED.findall((ENGINE / "DESIGN.txt").read_text())
    assert len(listed) > 20, "the scan is blind"
    assert not index_problems(listed, present_parts())


def test_every_cited_part_exists():
    files = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.decode().split("\0")
    present, seen = present_parts(), 0
    bad: list[str] = []
    for rel in files:
        p = ROOT / rel
        if not rel or p.suffix in SKIP_SUFFIXES or not p.is_file() or p == Path(__file__):
            continue
        text = p.read_text(errors="ignore")
        seen += len(CITED.findall(text))
        bad += [f"{rel}: {m}" for m in cited_problems(text, present)]
    assert seen > 100, "the scan is blind"
    assert not bad, "\n".join(bad)


def test_the_checks_can_fail():
    assert index_problems(["a.txt", "b.txt"], {"a.txt", "b.txt"}) == []
    assert index_problems(["a.txt", "a.txt"], {"a.txt"}) == ["a.txt is listed twice"]
    assert index_problems(["a.txt", "gone.txt"], {"a.txt"}) == ["gone.txt is listed but missing"]
    assert index_problems(["a.txt"], {"a.txt", "new.txt"}) == ["new.txt is not listed"]
    assert cited_problems('(engine design/a.txt, "Caps")', {"a.txt"}) == []
    assert len(cited_problems('(engine design/nope.txt, "Caps")', {"a.txt"})) == 1
