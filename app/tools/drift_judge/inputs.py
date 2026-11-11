"""What the judge reads, gathered by code from git and the repo: nothing here is chosen by a model."""
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
READOUTS = "app/tests/readouts"
ANCHOR = REPO / READOUTS / "ANCHOR"
DIRECTION = Path(__file__).resolve().parent / "direction.md"
DIFF_LINES = 1500
SUBJECTS = 300

_SHA = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class Inputs:
    head: str
    anchor: str
    before: str
    readout_diff: str
    cumulative_diff: str
    subjects: tuple[str, ...]
    omitted_subjects: int
    direction: str


class InputError(ValueError):
    pass


def git(*args: str, repo: Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def clip(text: str, limit: int = DIFF_LINES) -> str:
    """`text` cut to `limit` lines, saying how many it dropped, so a reader knows it is partial."""
    lines = text.splitlines()
    if len(lines) <= limit:
        return text
    return "\n".join(lines[:limit]) + f"\n[{len(lines) - limit} more lines omitted]"


def before_sha(given: str, repo: Path = REPO) -> str:
    """The tip main had before the merge just landed, when `given` names a commit; HEAD's parent otherwise."""
    if _SHA.fullmatch(given):
        known = subprocess.run(["git", "cat-file", "-e", f"{given}^{{commit}}"], cwd=repo, check=False)
        if known.returncode == 0:
            return given
    return git("rev-parse", "HEAD^", repo=repo).strip()


def read_anchor(path: Path = ANCHOR) -> str:
    sha = path.read_text().strip()
    if not _SHA.fullmatch(sha):
        raise InputError("ANCHOR is not a full commit sha")
    return sha


def gather(before_given: str = "", repo: Path = REPO, anchor_file: Path = ANCHOR) -> Inputs | None:
    """The judge's inputs, or None when no readout has changed since the anchor."""
    head = git("rev-parse", "HEAD", repo=repo).strip()
    anchor = read_anchor(anchor_file)
    pathspec = f"{READOUTS}/*.txt"
    cumulative = git("diff", anchor, head, "--", pathspec, repo=repo)
    if not cumulative.strip():
        return None
    before = before_sha(before_given, repo)
    readout_diff = git("diff", before, head, "--", pathspec, repo=repo)
    subjects = git("log", "--format=%s", f"{anchor}..{head}", repo=repo).splitlines()
    return Inputs(
        head=head, anchor=anchor, before=before,
        readout_diff=clip(readout_diff), cumulative_diff=clip(cumulative),
        subjects=tuple(subjects[:SUBJECTS]), omitted_subjects=max(0, len(subjects) - SUBJECTS),
        direction=DIRECTION.read_text(),
    )
