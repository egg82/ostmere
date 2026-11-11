"""The triggers still ahead and when each lands if nothing changes: what the page states as the next step (DESIGN.txt,
"Pending triggers"). Reads only."""
from collections.abc import Collection
from dataclasses import dataclass

from .conditions import is_true, unmet_rise_time
from .ids import TriggerId
from .orders import AtLeast, Condition, Unlocked
from .rules import Rules
from .state import Save
from .triggers import trigger_events
from .unlocks import Unlock


@dataclass(frozen=True)
class Pending:
    trigger: TriggerId
    at: int | None
    """When it fires under the segments now (trigger_events' time where its requires hold); an unmet require on an
    unlock waits for the earliest pending trigger that unlocks it. None: no time under the current segments."""
    held: bool
    """Every require holds now: only the condition stands between it and firing."""


def pending(save: Save, rules: Rules, only: Collection[str] | None = None) -> tuple[Pending, ...]:
    """Every unfired trigger whose requires hold, or whose unmet requires are each an unlock some unfired trigger
    gives, in rules order; restricted to `only` when given."""
    return _Reader(save, rules).pending(only)


class _Reader:
    def __init__(self, save: Save, rules: Rules) -> None:
        self.save, self.rules = save, rules
        self.timed = {e.subject: e.time for e in trigger_events(save, rules)}
        self.unfired = [i for i, fired in enumerate(save.fired) if not fired]
        self.givers: dict[Unlock, list[int]] = {}
        for i in self.unfired:
            for u in rules.triggers[i].outcome.unlocks:
                self.givers.setdefault(u, []).append(i)
        self.memo: dict[int, int | None] = {}
        self.open: set[int] = set()

    def pending(self, only: Collection[str] | None) -> tuple[Pending, ...]:
        triggers = self.rules.triggers
        out: list[Pending] = []
        for i in self.unfired:
            if only is not None and triggers[i].id not in only:
                continue
            unmet = [c for c in triggers[i].requires if not self._true(c)]
            if all(self._given(c) is not None for c in unmet):
                out.append(Pending(triggers[i].id, self.at(i), not unmet))
        return tuple(out)

    def at(self, i: int) -> int | None:
        if i in self.memo:
            return self.memo[i]
        t = self.rules.triggers[i]
        if t.id in self.timed:
            return self.memo.setdefault(i, self.timed[t.id])
        if i in self.open:
            return None
        self.open.add(i)
        times = [self._rise(t.when)] + [self._wait(c) for c in t.requires if not self._true(c)]
        self.open.discard(i)
        return self.memo.setdefault(i, None if None in times else max(x for x in times if x is not None))

    def _true(self, c: Condition) -> bool:
        return is_true(self.save, self.rules, c)

    def _rise(self, c: Condition) -> int | None:
        return self.save.time if self._true(c) else unmet_rise_time(self.save, self.rules, c)

    def _given(self, c: Condition) -> list[int] | None:
        """The unfired triggers that unlock what an AtLeast on an unlock needs; None for any other condition."""
        if not isinstance(c, AtLeast) or not isinstance(c.subject, Unlocked):
            return None
        return self.givers.get(c.subject.unlock) or None

    def _wait(self, c: Condition) -> int | None:
        givers = self._given(c)
        if givers is None:
            return None
        return min((t for j in givers if (t := self.at(j)) is not None), default=None)
