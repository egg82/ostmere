"""Every canon id (`C-<area>-<n>`) and decision id (`D-<n>`) cited anywhere in the repo's text is a row of
`content/canon/` (one file per area) or `content/decisions/` (one file per hundred ids), and both keep their row shape, so a new lead can take the
seat from them alone (docs/research/writing/studio-team.md, "What it means here").

A canon row's source is `file#heading`: the file is under `content/`, or under the repo root when it starts with
`docs/`; the heading is the start of a Markdown heading in it, or a top-level key of a YAML file. Only ids, fields and
paths are checked, never the wording of a fact or a decision."""
import json
import os
import re
from collections.abc import Mapping, Sequence
from pathlib import Path

REPO = Path(__file__).resolve().parent.parents[2]
CONTENT = REPO / "content"
SUFFIXES = frozenset({".py", ".ts", ".tsx", ".mjs", ".md", ".txt", ".toml", ".json", ".jsonl", ".yaml", ".yml"})
SKIPPED_DIRS = frozenset({".git", "node_modules", "build", "build-dev", "dist", "__pycache__", ".venv", "venv",
                          ".pytest_cache", ".hypothesis", "chapter-saves", "chapter-saves-cache"})
ID = re.compile(r"\b(?:C-[a-z]+-\d+|D-\d+)\b")
CANON_FIELDS = ("id", "area", "fact", "source", "status")
CANON_STATUSES = frozenset({"canon", "tentative"})
DECISION_FIELDS = ("id", "decision", "why", "date", "by", "status", "canon_ids")
DECISION_STATUSES = frozenset({"decided", "amended", "superseded", "open", "accepted"})
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEADING = re.compile(r"(?m)^#+ (.+?)\s*$")
YAML_KEY = re.compile(r"(?m)^([\w-]+):")
FLOOR = 400  # distinct ids cited when the gate arrived: about 470


def cited(root: Path) -> dict[str, str]:
    """Each id cited under `root` -> the first file citing it. This file plants ids of its own, so it is left out."""
    found: dict[str, str] = {}
    for directory, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        for name in files:
            path = Path(directory) / name
            if path.suffix in SUFFIXES and path != Path(__file__).resolve():
                for token in ID.findall(path.read_text(encoding="utf-8", errors="replace")):
                    found.setdefault(token, str(path.relative_to(root)))
    return found


def rows(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canon_rows(content: Path) -> list[dict[str, object]]:
    """Every canon row, area by area (file name order), each area's rows in file order."""
    return [row for path in sorted((content / "canon").glob("*.jsonl")) for row in rows(path)]


def decision_rows(content: Path) -> list[dict[str, object]]:
    """Every decision row, file by file (name order: one file per hundred ids), each file's rows in file order."""
    return [row for path in sorted((content / "decisions").glob("*.jsonl")) for row in rows(path)]


def misfiled(content: Path) -> list[str]:
    """Canon rows sitting in a file that is not their area's."""
    return [f"{path.name}: {r.get('id')} is area {r.get('area')!r}"
            for path in sorted((content / "canon").glob("*.jsonl")) for r in rows(path) if r.get("area") != path.stem]


def dangling(found: dict[str, str], known: set[str]) -> list[str]:
    return sorted(f"{where}: {token} has no row" for token, where in found.items() if token not in known)


def source_resolves(source: str, content: Path, repo: Path) -> bool:
    name, _, part = source.partition("#")
    path = (repo if name.startswith("docs/") else content) / name
    if not part or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        return part in YAML_KEY.findall(text)
    return any(h == part or (h.startswith(part) and not h[len(part)].isalnum()) for h in HEADING.findall(text))


def canon_problems(canon: Sequence[Mapping[str, object]], content: Path, repo: Path) -> list[str]:
    wrong = [f"{r.get('id')}: fields {list(r)}" for r in canon if tuple(r) != CANON_FIELDS]
    wrong += [f"{r.get('id')}: status {r.get('status')!r}" for r in canon if r.get("status") not in CANON_STATUSES]
    wrong += [f"{r.get('id')}: source {r.get('source')!r} resolves to no file and heading"
              for r in canon if not source_resolves(str(r.get("source")), content, repo)]
    return wrong + duplicates(canon)


def decision_problems(log: Sequence[Mapping[str, object]]) -> list[str]:
    wrong = [f"{r.get('id')}: fields {list(r)}" for r in log if tuple(r)[:len(DECISION_FIELDS)] != DECISION_FIELDS
             or not set(r) <= {*DECISION_FIELDS, "accepts"}]
    wrong += [f"{r.get('id')}: status {r.get('status')!r}" for r in log if r.get("status") not in DECISION_STATUSES]
    wrong += [f"{r.get('id')}: date {r.get('date')!r}" for r in log if not DATE.match(str(r.get("date")))]
    wrong += [f"{r.get('id')}: empty by" for r in log if not r.get("by")]
    return wrong + duplicates(log)


def duplicates(table: Sequence[Mapping[str, object]]) -> list[str]:
    ids = [str(r.get("id")) for r in table]
    return sorted({f"{i}: used by {ids.count(i)} rows" for i in ids if ids.count(i) > 1})


def known_ids() -> set[str]:
    return {str(r["id"]) for r in [*canon_rows(CONTENT), *decision_rows(CONTENT)]}


def test_every_cited_id_has_a_row() -> None:
    found = cited(REPO)
    assert len(found) >= FLOOR, f"read {len(found)} distinct ids, expected at least {FLOOR}: the scan sees too little"
    assert not dangling(found, known_ids()), "\n".join(dangling(found, known_ids()))


def test_canon_rows_keep_their_shape_and_sources() -> None:
    canon = canon_rows(CONTENT)
    assert len(canon) >= 290, f"read {len(canon)} canon rows: too few"
    assert not misfiled(CONTENT), "\n".join(misfiled(CONTENT))
    assert not canon_problems(canon, CONTENT, REPO), "\n".join(canon_problems(canon, CONTENT, REPO))


def test_decision_rows_keep_their_shape() -> None:
    log = decision_rows(CONTENT)
    assert len(log) >= 100, f"read {len(log)} decision rows: too few"
    assert not decision_problems(log), "\n".join(decision_problems(log))


def test_the_gate_fails_on_planted_faults(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("# Top\n\n## Real heading, long\n")
    (tmp_path / "b.yaml").write_text("beats:\n  nested: 1\n")
    (tmp_path / "plan.md").write_text("Per D-7 and C-beat-1; see C-beat-99 (not D-77x or AC-beat-3).\n")
    found = cited(tmp_path)
    assert set(found) == {"D-7", "C-beat-1", "C-beat-99"}
    assert dangling(found, {"D-7", "C-beat-1"}) == ["plan.md: C-beat-99 has no row"]
    good = {"id": "C-beat-1", "area": "beat", "fact": "f", "source": "docs/a.md#Real heading", "status": "canon"}
    assert canon_problems([good, {**good, "id": "C-beat-2", "source": "b.yaml#beats"}], tmp_path, tmp_path) == []
    bad = [{**good, "source": "docs/a.md#Real head"}, {**good, "id": "C-x-1", "source": "b.yaml#nested"},
           {**good, "id": "C-x-2", "status": "proposed"}, {**good, "id": "C-x-2"}]
    assert len(canon_problems(bad, tmp_path, tmp_path)) == 4
    row: dict[str, object] = {"id": "D-7", "decision": "d", "why": "w", "date": "2026-11-16", "by": "lead",
                              "status": "decided", "canon_ids": []}
    assert decision_problems([row, {**row, "id": "D-8", "accepts": list[object]()}]) == []
    broken: list[dict[str, object]] = [{"id": "D-1", "decision": "d", "why": "w"}, {**row, "id": "D-2", "status": "x"},
                                       {**row, "id": "D-3", "date": ""}, {**row, "id": "D-4", "extra": 1}]
    assert len(decision_problems(broken)) == 7
    (tmp_path / "canon").mkdir()
    (tmp_path / "canon" / "beat.jsonl").write_text(json.dumps(good) + "\n" + json.dumps({**good, "id": "C-world-1", "area": "world"}) + "\n")
    assert canon_rows(tmp_path) == [good, {**good, "id": "C-world-1", "area": "world"}]
    assert misfiled(tmp_path) == ["beat.jsonl: C-world-1 is area 'world'"]
    (tmp_path / "decisions").mkdir()
    (tmp_path / "decisions" / "d-100.jsonl").write_text(json.dumps({**row, "id": "D-101"}) + "\n")
    (tmp_path / "decisions" / "d-000.jsonl").write_text(json.dumps(row) + "\n")
    assert [r["id"] for r in decision_rows(tmp_path)] == ["D-7", "D-101"]
