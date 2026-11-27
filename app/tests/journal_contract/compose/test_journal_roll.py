"""`roll`: the documented hash, in [0, 1), keyed by every part of its key, and the same in any process (statements 1
and 6, and `roll`'s docstring)."""
import os
import subprocess
import sys
from pathlib import Path

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import Purpose, roll
from journal_world import ref_roll

PURPOSES: tuple[Purpose, ...] = ("write", "late", "misremember", "mark")
HERE = Path(__file__).parent.parent
APP = HERE.parent.parent

ids = st.text(st.characters(codec="utf-8", exclude_categories=("Cs",)), min_size=1, max_size=12)


@given(save_id=st.integers(0, 2**62), day=st.integers(0, 10_000), subject=ids, purpose=st.sampled_from(PURPOSES))
def test_roll_is_the_documented_hash(save_id: int, day: int, subject: str, purpose: Purpose):
    """Statement 1 and `roll`'s docstring: SHA-256 of "save|journal|day|subject|purpose", its first eight bytes over
    2**64."""
    assert roll(save_id, day, subject, purpose) == ref_roll(save_id, day, subject, purpose)


@given(save_id=st.integers(0, 2**62), day=st.integers(0, 10_000), subject=ids, purpose=st.sampled_from(PURPOSES))
def test_roll_is_in_the_unit_interval(save_id: int, day: int, subject: str, purpose: Purpose):
    """`roll`'s docstring: a draw in [0, 1)."""
    assert 0.0 <= roll(save_id, day, subject, purpose) < 1.0


def test_roll_is_keyed_by_each_part():
    """Statement 6: a draw depends on its save, day, subject and purpose, so no draw stands in for another."""
    base = roll(7, 3, "kettle", "write")
    others = [roll(8, 3, "kettle", "write"), roll(7, 4, "kettle", "write"), roll(7, 3, "kettles", "write")]
    others += [roll(7, 3, "kettle", p) for p in PURPOSES if p != "write"]
    assert len({base, *others}) == 1 + len(others)


def test_roll_known_values():
    """`roll`'s docstring, two values worked from hashlib once, so a wrong byte order or join fails by name."""
    assert roll(1, 0, "a", "write") == 0.21387594600223858
    assert roll(42, 7, "kettle", "late") == 0.008445488578189908


def _in_fresh_process(code: str, hash_seed: str) -> str:
    env = {**os.environ, "PYTHONHASHSEED": hash_seed, "PYTHONPATH": f"{APP}{os.pathsep}{HERE}"}
    done = subprocess.run([sys.executable, "-c", code], env=env, cwd=APP, capture_output=True, text=True, timeout=20)
    assert done.returncode == 0, done.stderr
    return done.stdout


ROLLS = "from ashfall_app.saves.journal import roll\nprint([roll(s, 9, 'k', 'write') for s in range(9)])"
SPAN = "from journal_mixed import composed\nprint(repr(composed()))"


def test_roll_is_the_same_in_another_process():
    """Statement 1: no salted `hash()`, so another process with another hash seed draws the same."""
    assert _in_fresh_process(ROLLS, "1") == _in_fresh_process(ROLLS, "2")


def test_a_span_composes_the_same_in_another_process():
    """Statement 1: the same arguments give an equal result in any process (subject ids are strings, whose `hash()` is
    salted per process, so a set or dict order leaking into the notes shows here)."""
    from journal_mixed import composed
    assert _in_fresh_process(SPAN, "1") == _in_fresh_process(SPAN, "3") == repr(composed()) + "\n"
