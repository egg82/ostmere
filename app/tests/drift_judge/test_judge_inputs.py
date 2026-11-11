"""The inputs, gathered from a throwaway git repository: the merge's diff, the diff since the anchor, the subjects between."""
import subprocess
from pathlib import Path

import pytest

from tools.drift_judge.inputs import InputError, before_sha, clip, gather, read_anchor


def git(repo: Path, *args: str) -> str:
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x",
           "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(repo)}
    return subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True).stdout.strip()


def commit(repo: Path, subject: str, **files: str) -> str:
    for name, text in files.items():
        path = repo / "app/tests/readouts" / name if name.endswith(".txt") else repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", subject)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    return tmp_path


def history(repo: Path) -> tuple[str, str, str]:
    """(anchor, the commit before the last, head): three readout versions, the anchor's first."""
    anchor = commit(repo, "ashfall tests: first", **{"opening.txt": "run 3\n"})
    middle = commit(repo, "ashfall content: second", **{"opening.txt": "run 5\n"})
    head = commit(repo, "ashfall tests: third", **{"opening.txt": "run 9\n"})
    return anchor, middle, head


def anchored(repo: Path, tmp_path: Path, sha: str) -> Path:
    anchor_file = tmp_path / "ANCHOR"
    anchor_file.write_text(sha + "\n")
    return anchor_file


def test_the_merge_diff_is_the_push_and_the_cumulative_diff_runs_from_the_anchor(repo: Path, tmp_path: Path) -> None:
    anchor, middle, head = history(repo)
    got = gather(middle, repo, anchored(repo, tmp_path, anchor))
    assert got is not None
    assert (got.head, got.anchor, got.before) == (head, anchor, middle)
    assert "-run 5" in got.readout_diff and "-run 3" not in got.readout_diff
    assert "-run 3" in got.cumulative_diff and "+run 9" in got.cumulative_diff
    assert got.subjects == ("ashfall tests: third", "ashfall content: second")
    assert got.omitted_subjects == 0 and "the owner" in got.direction


def test_no_readout_change_since_the_anchor_gathers_nothing(repo: Path, tmp_path: Path) -> None:
    _, _, head = history(repo)
    commit(repo, "ashfall docs: words", **{"docs.md": "x\n"})
    assert gather("", repo, anchored(repo, tmp_path, head)) is None


def test_a_moved_anchor_file_alone_is_not_a_readout_change(repo: Path) -> None:
    _, _, head = history(repo)
    commit(repo, "ashfall tests: anchor moved", ANCHOR=head + "\n")
    assert gather("", repo, repo / "ANCHOR") is None


@pytest.mark.parametrize("text", ["", "main", "abc123", "A" * 40, "g" * 40])
def test_an_anchor_that_is_not_a_full_sha_is_an_input_error(text: str, tmp_path: Path) -> None:
    f = tmp_path / "ANCHOR"
    f.write_text(text)
    with pytest.raises(InputError):
        read_anchor(f)


@pytest.mark.parametrize("given", ["", "0" * 40, "f" * 40, "not-a-sha"])
def test_an_unusable_before_sha_falls_back_to_the_head_parent(given: str, repo: Path) -> None:
    _, middle, _ = history(repo)
    assert before_sha(given, repo) == middle


def test_a_long_diff_is_cut_with_the_count_it_lost() -> None:
    text = "\n".join(str(n) for n in range(10))
    assert clip(text, 10) == text
    assert clip(text, 4) == "0\n1\n2\n3\n[6 more lines omitted]"
