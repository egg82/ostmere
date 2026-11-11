"""The per-test time gate (conftest.py): its verdict function can fail, a wait is not CPU, and the held list stays empty."""
import time

from tests import conftest


def test_over_the_ceiling_is_slow():
    assert conftest.too_slow("tests/x.py::t", conftest.CEILING_S + 0.01)


def test_under_the_ceiling_is_fine():
    assert not conftest.too_slow("tests/x.py::t", conftest.CEILING_S)


def test_held_tests_are_excused_and_the_list_stays_empty():
    assert conftest.too_slow("tests/x.py::t", 99)
    assert not conftest.HELD, "HELD may only shrink; it starts empty, so it stays empty"


def test_waiting_is_not_cpu():
    start = conftest.cpu_now()
    time.sleep(0.3)
    assert conftest.cpu_now() - start < 0.1
