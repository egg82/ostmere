"""The loss runners' lost tallies at each day's end a step passes (api/contract/loss-lines.txt, "LOSS LINES"): read off the save the
step began from, advanced to that second. Engine invariant 81 makes that the save however the steps fell, so a day's
loss notes do not depend on when the player looked. A tally only grows, so when it holds the same whole number at the
step's start and end, no advance is needed."""
from .. import engine as e
from .journal import Loss
from .journal_rules import LossRunner


class Tallies:
    """Asked for day ends in ascending order, each at most the step's end."""

    def __init__(self, began: e.Save, after: e.Save, rules: e.Rules, runners: tuple[LossRunner, ...]) -> None:
        self._rules, self._runners = rules, runners
        self._cursor, self._end = began, after.time
        self._began, self._after = self._read(began), self._read(after)

    def at(self, t: int) -> tuple[Loss, ...]:
        """Each runner's lost tally floored at game second `t`. A second before the step began (a save composing days
        from before its journal was kept) reads the tally the step began with."""
        if not self._runners:
            return ()
        if self._began == self._after or t >= self._end:
            lost = self._after
        elif t <= self._cursor.time:
            lost = self._read(self._cursor)
        else:
            self._cursor = e.advance(self._cursor, self._rules, t)
            lost = self._read(self._cursor)
        return tuple(Loss(r.runner, r.keys, n) for r, n in zip(self._runners, lost, strict=True))

    def _read(self, save: e.Save) -> tuple[int, ...]:
        return tuple(e.segment(save, self._rules, e.StoreId(r.tally)).start_value // e.QUANTITY_SCALE
                     for r in self._runners)
