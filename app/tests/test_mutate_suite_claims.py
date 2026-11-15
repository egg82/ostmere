"""The mutation tool reads @kills claims from a suite's own files and from the files it runs beside them."""
from pathlib import Path

import pytest

from tools import mutate_suite as ms


def test_a_claim_is_read_from_the_suites_own_files_and_from_also(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    (tmp_path / "home").mkdir()
    (tmp_path / "beside").mkdir()
    (tmp_path / "home" / "test_own.py").write_text("@kills(1)\ndef test_a(): ...\n")
    (tmp_path / "beside" / "test_other.py").write_text("@kills(2, 9)\n@kills(3)\ndef test_b(): ...\n\ndef test_c(): ...\n")
    monkeypatch.setattr(ms, "APP", tmp_path)
    suite = ms.Suite("MUTANTS_x.txt", "test_own.py", "x_mutants", 1, 3, ("beside/test_*.py",), home="home")
    assert ms.claims(suite) == {1: ["home/test_own.py::test_a"], 2: ["beside/test_other.py::test_b"],
                                3: ["beside/test_other.py::test_b"]}
