"""The approval snapshot (readout_snapshot.py) on readouts in a temporary directory: an unchanged text passes, a planted
changed line fails with its diff and the new text written for the job's artifact, an empty or uncommitted readout
fails, and a package's committed files are matched to the readouts it writes."""
from pathlib import Path

import pytest

from tests import readout_snapshot as rs

TEXT = "typical\n  V1 new 3 decisions 1\n  V2 new 4 decisions 2\n"


def test_an_unchanged_readout_passes(tmp_path: Path):
    rs.write("dayone-x", TEXT, tmp_path)
    rs.check("dayone-x", TEXT, tmp_path)


def test_a_changed_line_fails_with_its_diff_and_the_new_text_is_written(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    rs.write("dayone-x", TEXT, tmp_path)
    out = tmp_path / "new"
    monkeypatch.setenv(rs.OUT_ENV, str(out))
    planted = TEXT.replace("decisions 2", "decisions 0")
    with pytest.raises(AssertionError) as e:
        rs.check("dayone-x", planted, tmp_path)
    assert "-  V2 new 4 decisions 2" in str(e.value) and "+  V2 new 4 decisions 0" in str(e.value)
    assert "--write dayone" in str(e.value)
    assert rs.path("dayone-x", out).read_text() == planted
    assert rs.path("dayone-x", tmp_path).read_text() == TEXT


def test_an_uncommitted_readout_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(rs.OUT_ENV, raising=False)
    with pytest.raises(AssertionError, match="changed"):
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
