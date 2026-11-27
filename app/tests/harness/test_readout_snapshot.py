"""The readout report (readout_snapshot.py) on readouts in a temporary directory: an unchanged text reports nothing, a
planted changed line is reported with its diff and the new text written for the job's artifact but does not fail, an
uncommitted readout is reported, an empty one fails, and a package's committed files are matched to the readouts it
writes."""
import warnings
from pathlib import Path

import pytest

from tests import readout_snapshot as rs

TEXT = "typical\n  V1 new 3 decisions 1\n  V2 new 4 decisions 2\n"


def test_an_unchanged_readout_reports_nothing(tmp_path: Path):
    rs.write("dayone-x", TEXT, tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("error", rs.ReadoutChanged)
        assert rs.check("dayone-x", TEXT, tmp_path) == []


def test_a_changed_line_is_reported_with_its_diff_and_the_new_text_is_written(tmp_path: Path,
                                                                            monkeypatch: pytest.MonkeyPatch):
    rs.write("dayone-x", TEXT, tmp_path)
    out = tmp_path / "new"
    monkeypatch.setenv(rs.OUT_ENV, str(out))
    planted = TEXT.replace("decisions 2", "decisions 0")
    with pytest.warns(rs.ReadoutChanged) as seen:
        diff = rs.check("dayone-x", planted, tmp_path)
    shown = str(seen[0].message)
    assert "-  V2 new 4 decisions 2" in shown and "+  V2 new 4 decisions 0" in shown
    assert "--write dayone" in shown
    assert "-  V2 new 4 decisions 2" in diff
    assert rs.path("dayone-x", out).read_text() == planted
    assert rs.path("dayone-x", tmp_path).read_text() == TEXT


def test_a_long_diff_is_cut_to_its_head(tmp_path: Path):
    long = "".join(f"line {n}\n" for n in range(rs.SHOWN * 2))
    with pytest.warns(rs.ReadoutChanged) as seen:
        rs.check("dayone-x", long, tmp_path)
    shown = str(seen[0].message)
    assert f"line {rs.SHOWN - 5}" in shown and f"line {rs.SHOWN * 2 - 1}" not in shown and "more lines" in shown


def test_an_uncommitted_readout_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(rs.OUT_ENV, raising=False)
    with pytest.warns(rs.ReadoutChanged, match="changed"):
        rs.check("dayone-x", TEXT, tmp_path)


def test_an_empty_readout_fails(tmp_path: Path):
    rs.write("dayone-x", "\n", tmp_path)
    with pytest.raises(AssertionError, match="rendered nothing"):
        rs.check("dayone-x", "\n", tmp_path)


def test_stray_names_committed_files_nothing_writes_and_readouts_never_committed(tmp_path: Path):
    for name in ("dayone-a", "dayone-gone", "daytwo-a", "dayonex"):
        rs.write(name, TEXT, tmp_path)
    assert rs.stray("dayone", ("dayone-a", "dayone-new"), tmp_path) == (["dayone-gone"], ["dayone-new"])


def test_every_package_names_a_report_module_with_names_of_its_own():
    for package in rs.PACKAGES:
        names = rs.module(package).NAMES
        assert names and all(n == package or n.startswith(package + "-") for n in names), package
