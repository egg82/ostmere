"""`python -m tools.drift_judge --brief`: the brief holds what the subagent judges from, and says so when there is none."""
import pytest

from tools.drift_judge.__main__ import main
from tools.drift_judge.inputs import Inputs
from tools.drift_judge.prompt import NOTHING, brief

FOUND = Inputs(head="b" * 40, anchor="a" * 40, before="c" * 40, readout_diff="+ merge-line", cumulative_diff="+ since-anchor-line",
               subjects=("ashfall tests: one", "ashfall content: two"), omitted_subjects=3, direction="direction text")


def test_the_brief_holds_the_direction_the_subjects_and_both_diffs() -> None:
    text = brief(FOUND)
    for part in ("direction text", "ashfall tests: one", "ashfall content: two", "+ since-anchor-line", "+ merge-line",
                 "[3 older subjects omitted]", "a" * 40, "b" * 40, "Never spoil the owner"):
        assert part in text


def test_the_cumulative_diff_sits_in_its_own_section_and_the_merge_diff_in_its_own() -> None:
    text = brief(FOUND)
    cumulative = text.split("<cumulative_readout_diff_since_anchor>")[1].split("</cumulative_readout_diff_since_anchor>")[0]
    assert "since-anchor-line" in cumulative and "merge-line" not in cumulative


def none(before: str) -> None:
    return None


def test_no_readout_change_prints_the_nothing_to_judge_line(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("tools.drift_judge.__main__.gather", none)
    assert main(["--brief"]) == 0
    assert capsys.readouterr().out == NOTHING + "\n"


def test_a_change_prints_the_brief_and_passes_the_before_sha_on(monkeypatch: pytest.MonkeyPatch,
                                                                capsys: pytest.CaptureFixture[str]) -> None:
    seen: list[str] = []

    def fake(before: str) -> Inputs:
        seen.append(before)
        return FOUND

    monkeypatch.setattr("tools.drift_judge.__main__.gather", fake)
    assert main(["--brief", "c" * 40]) == 0
    assert seen == ["c" * 40] and "direction text" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [[], ["--controls"], ["--brief", "x", "y"]])
def test_other_arguments_exit_two(argv: list[str]) -> None:
    assert main(argv) == 2
