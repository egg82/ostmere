"""Invariant 18: the engine package imports only the stdlib and itself, and no nondeterminism or I/O module.

A structural test: it parses every module under ashfall_app/engine/. The checker is proven able to fail by running it
over planted files (non-stdlib, the app's own modules, random/time/datetime) and proven not to cry wolf over a clean
one."""
import ast
import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[2] / "ashfall_app" / "engine"
PACKAGE = "ashfall_app.engine"
STDLIB = sys.stdlib_module_names
NONDETERMINISTIC_OR_IO = {
    "random", "secrets", "time", "datetime", "uuid", "os", "pathlib", "socket", "subprocess", "shutil", "sqlite3",
    "urllib", "http", "asyncio", "threading", "multiprocessing", "tempfile", "importlib", "ctypes", "signal",
}


def violations(path: Path) -> list[str]:
    """Every import in `path` (at any nesting depth, TYPE_CHECKING blocks included) the engine may not make."""
    out: list[str] = []
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                continue  # relative: inside the package
            base = node.module or ""
            mods = [base] + [f"{base}.{a.name}" for a in node.names if base == "ashfall_app"]
        elif isinstance(node, ast.Call) and getattr(node.func, "id", "") in ("__import__", "exec", "eval"):
            out.append(f"{path.name}:{node.lineno}: dynamic import/eval")
            continue
        else:
            continue
        for m in mods:
            top = m.split(".")[0]
            if top in NONDETERMINISTIC_OR_IO:
                out.append(f"{path.name}:{node.lineno}: {m} (nondeterminism or I/O)")
            elif top == "ashfall_app":
                if not (m == PACKAGE or m.startswith(PACKAGE + ".") or m == "ashfall_app"):
                    out.append(f"{path.name}:{node.lineno}: {m} (outside the engine package)")
            elif top not in STDLIB:
                out.append(f"{path.name}:{node.lineno}: {m} (not stdlib)")
    return out


def engine_files() -> list[Path]:
    return sorted(ENGINE.rglob("*.py"))


def test_the_checker_sees_the_engine():
    """Invariant 18 (purity): the scan examines the real package (a clean pass over zero files is not a pass)."""
    names = {p.name for p in engine_files()}
    assert {"__init__.py", "api.py", "rules.py", "state.py", "units.py"} <= names
    assert len(names) >= 10


def test_engine_imports_only_stdlib_and_itself():
    """Invariant 18 (purity): no module in ashfall_app/engine/ imports anything but the stdlib and the package."""
    found = [v for p in engine_files() for v in violations(p)]
    assert not found, found


@pytest.mark.parametrize("src, needle", [
    ("import fastapi\n", "fastapi"),
    ("from fastapi import FastAPI\n", "fastapi"),
    ("import ashfall_app.main\n", "ashfall_app.main"),
    ("from ashfall_app.main import app\n", "ashfall_app.main"),
    ("from ashfall_app import main\n", "ashfall_app.main"),
    ("import random\n", "random"),
    ("from random import Random\n", "random"),
    ("import time\n", "time"),
    ("from datetime import datetime\n", "datetime"),
    ("import os.path\n", "os"),
    ("def f():\n    import httpx\n", "httpx"),
    ("from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import numpy\n", "numpy"),
    ("x = __import__('requests')\n", "dynamic"),
])
def test_planted_violations_are_caught(tmp_path: Path, src: str, needle: str):
    """Invariant 18 (purity): the checker can fail. Each planted forbidden import is reported."""
    f = tmp_path / "planted.py"
    f.write_text(src)
    found = violations(f)
    assert found and needle in found[0], found


def test_clean_imports_are_not_flagged(tmp_path: Path):
    """Invariant 18 (purity): the checker does not cry wolf on stdlib, relative and in-package imports."""
    f = tmp_path / "clean.py"
    f.write_text("import dataclasses\nfrom enum import IntEnum\nfrom typing import NewType\nfrom fractions import Fraction\n"
                 "from .ids import StoreId\nfrom ..engine import api\nfrom ashfall_app.engine import units\n"
                 "import ashfall_app.engine.rules\nfrom ashfall_app.engine.state import Save\nimport math, functools\n")
    assert violations(f) == []
