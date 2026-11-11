"""A trigger whose require on an unlock fails costs one look each time the save's fired or unlocked set changes,
never one per instant: a chain of offers each waiting on the last one's answer grows with every chapter, and read at
every instant it made the bench's steps slower in proportion (engine-bench, day twelve). Counts, not seconds."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AfterTime, AtLeast, Outcome, Rules, Save, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, advance,
)
from ashfall_app.engine import triggers
from tests.opening.playthrough import Player, opening_rules

BLOCKED = 40
SPAN_S = 600


@pytest.fixture(scope="module")
def played() -> tuple[Save, Rules, Rules]:
    """The scripted player's save after its last decision (its mix running), the shipped rules, and those rules with
    BLOCKED triggers that hold from the start and require an unlock nothing lands."""
    base = opening_rules()
    p = Player(base)
    p.play()
    blocked = tuple(TriggerDef(TriggerId(f"t_blocked_{i}"), AfterTime(0), Outcome(),
                               requires=(AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, f"never_{i}")), 1, 1),))
                    for i in range(BLOCKED))
    more = replace(base, triggers=base.triggers + blocked)
    advance(replace(p.save, fired=p.save.fired + (False,) * BLOCKED), more, p.save.time + 1)  # its indexes, built here
    return p.save, base, more


def _looks(monkeypatch: pytest.MonkeyPatch, save: Save, rules: Rules) -> tuple[int, int]:
    """(condition reads in triggers.py, _unfired builds) over SPAN_S of the mix."""
    extra = len(rules.triggers) - len(save.fired)
    start = replace(save, fired=tuple([*save.fired, *[False] * extra]))  # a new tuple: no memo holds it
    counts = {"reads": 0, "builds": 0}

    def count(name: str, key: str) -> None:
        real: Callable[..., object] = getattr(triggers, name)

        def counted(*a: object) -> object:
            counts[key] += 1
            return real(*a)
        monkeypatch.setattr(triggers, name, counted)

    count("is_true", "reads")
    count("all_true", "reads")
    count("_unfired", "builds")
    end = advance(start, rules, start.time + SPAN_S)
    monkeypatch.undo()
    assert end.fired[len(save.fired):] == (False,) * extra
    return counts["reads"], counts["builds"]


def test_a_blocked_trigger_is_read_once_per_change_of_unlocks_not_per_instant(
        monkeypatch: pytest.MonkeyPatch, played: tuple[Save, Rules, Rules]) -> None:
    save, base, more = played
    reads, builds = _looks(monkeypatch, save, base)
    more_reads, more_builds = _looks(monkeypatch, save, more)
    assert builds == more_builds and builds > 0
    assert reads > 10 * builds, "control: the span has many instants per build, so a per-instant read would show"
    assert more_reads - reads <= BLOCKED * builds
