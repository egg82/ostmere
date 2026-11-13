"""The collection rule each play-owning conftest applies to its play fixtures (tests/<dir>/conftest.py)."""
import pytest


def mark_plays(items: list[pytest.Item], plays: frozenset[str], timeout_s: float | None) -> None:
    """The split between the `tests` and `playthrough` jobs is a gate, not a habit: a test reading one of `plays`
    without the playthrough marker fails collection. A play is a session fixture, so its setup is charged to whichever
    test first requests it: with `timeout_s`, every reader runs under at least that timeout, whatever its file marks;
    without, the plays fit pytest.ini's. A play is pure Python on the main thread, so its timeout is a signal: the test
    fails with the traceback of where the play was, and its xdist worker lives to report it (pytest.ini's thread
    method exits the worker, which leaves only "node down" and a job waiting out its own timeout)."""
    for item in items:
        uses = plays & set(getattr(item, "fixturenames", ()))
        if not uses:
            continue
        if item.get_closest_marker("playthrough") is None:
            raise pytest.UsageError(f"{item.nodeid} reads {sorted(uses)} but is not marked playthrough")
        if timeout_s is not None:
            item.add_marker(pytest.mark.timeout(max(timeout_s, own_timeout(item)), method="signal"), append=False)


def own_timeout(item: pytest.Item) -> float:
    marker = item.get_closest_marker("timeout")
    return float(marker.args[0]) if marker is not None and marker.args else 0.0
