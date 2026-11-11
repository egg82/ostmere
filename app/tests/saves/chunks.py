"""Shared by the chunked-catch-up suites: golden saves under today's opening, stop patterns, and a chain of bounded
advances resumed the way the database resumes them (each from the previous Step's save, through encode and decode)."""
import random
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from ashfall_app import engine as e
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import load_opening, to_rules

GOLDEN = Path(__file__).resolve().parent / "golden"
DAY_S = 86_400
MAX_CALLS = 3000
"""A chain that has not ended after this many calls is not making progress."""

Stop = Callable[[], bool]
MakeStop = Callable[[], Stop]
"""One stop per call, as the service asks `stop_for` once per request."""


@cache
def todays_rules() -> e.Rules:
    return to_rules(load_opening())


def golden(name: str, rules: e.Rules | None = None) -> e.Save:
    """A golden save (`f7/05-seed0-end526`) under today's opening (or `rules`), rebased if written under older rules."""
    text = (GOLDEN / f"{name}.json").read_text().strip()
    return e.rebase(text, rules or todays_rules(), engine_renames(load_renames()))


def never() -> Stop:
    return lambda: False


def always() -> Stop:
    return lambda: True


def every(k: int) -> MakeStop:
    """Each call stops after its k-th instant."""
    def make() -> Stop:
        seen = 0

        def stop() -> bool:
            nonlocal seen
            seen += 1
            return seen % k == 0
        return stop
    return make


def irregular(seed: int, p: float = 0.3) -> MakeStop:
    """One seeded stream across all the calls: a stop falls wherever the dice say."""
    rng = random.Random(seed)
    return lambda: (lambda: rng.random() < p)


def counting(inner: Stop, counts: list[int]) -> Stop:
    def stop() -> bool:
        counts.append(1)
        return inner()
    return stop


@dataclass(frozen=True)
class Chained:
    final: str
    """The last save, encoded."""
    lines: tuple[e.Line, ...]
    changes: tuple[e.RuleChange, ...]
    times: tuple[int, ...]
    """The save's time after each call."""
    stopped: tuple[bool, ...]


def chain(start: e.Save, rules: e.Rules, t: int, make_stop: MakeStop) -> Chained:
    """Bounded advances to t until one is not stopped short. Each stopped call must have moved the save forward and
    stayed before t; a call that did neither would never end."""
    save = e.decode(e.encode(start, rules), rules)
    lines: list[e.Line] = []
    changes: list[e.RuleChange] = []
    times: list[int] = []
    stopped: list[bool] = []
    for _ in range(MAX_CALLS):
        step = e.advance_logged(save, rules, t, make_stop())
        lines.extend(step.lines)
        changes.extend(step.rule_changes)
        times.append(step.save.time)
        stopped.append(step.stopped_short)
        if not step.stopped_short:
            assert step.save.time == t, f"caught up but at {step.save.time}, not {t}"
            return Chained(e.encode(step.save, rules), tuple(lines), tuple(changes), tuple(times), tuple(stopped))
        assert save.time < step.save.time < t, f"stopped short without progress or before it: {save.time} -> {step.save.time} (t={t})"
        save = e.decode(e.encode(step.save, rules), rules)
    raise AssertionError(f"not caught up after {MAX_CALLS} calls: last at {times[-1]} of {t}")
