"""Each heavy step's reading (counters.decides) of a chapter, all started at once in processes forked from this one, so
they share its play without replaying it: the readings are most of week two's job (day twelve's are minutes each) and
none needs another. A part's test (verdicts.decided_in) waits for its own steps only."""
import os
from concurrent.futures import Future, ProcessPoolExecutor
from multiprocessing import get_context

from ashfall_app.engine import Rules
from tests.daythree.counters import Step
from tests.weektwo import counters

Key = tuple[str, int]
"""(visit label, step index)."""
_FORKED: dict[Key, tuple[Step, Rules]] = {}
"""What the forked processes read: set before the pool forks, so each inherits it."""


def _decides(key: Key) -> bool:
    step, rules = _FORKED[key]
    return counters.decides(step, rules)


def started(steps: dict[Key, Step], rules: Rules) -> dict[Key, Future[bool]]:
    """Each step's reading, started in key order on a pool of one process per CPU this process may run on."""
    _FORKED.clear()
    _FORKED.update({key: (step, rules) for key, step in steps.items()})
    workers = max(1, min(len(steps), len(os.sched_getaffinity(0))))
    pool = ProcessPoolExecutor(max_workers=workers, mp_context=get_context("fork"))
    found = {key: pool.submit(_decides, key) for key in steps}
    pool.shutdown(wait=False)   # the submitted readings still run; the processes exit once they are done
    return found
