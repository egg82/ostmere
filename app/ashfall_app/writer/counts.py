"""Where the queue keeps a day's counts: per world, its weight (a visit) and the calls spent. Rows of past days are
the store's to drop when a new day's visit arrives."""

from datetime import date
from typing import Protocol


class DayCounts(Protocol):
    def load(self, day: date) -> tuple[dict[str, int], dict[str, int]]:
        """(weights, spent) of the worlds visited on `day`, by save id."""
        ...

    def visit(self, day: date, save_id: str, weight: int) -> None:
        """Sets the world's weight for `day`, keeping what it has spent, and drops every earlier day."""
        ...

    def spend(self, day: date, save_id: str) -> None:
        """One more call spent by the world on `day`."""
        ...


class MemoryCounts:
    """The default: counts live in this process."""

    def __init__(self) -> None:
        self._day: date | None = None
        self._visits: dict[str, int] = {}
        self._spent: dict[str, int] = {}

    def load(self, day: date) -> tuple[dict[str, int], dict[str, int]]:
        if day != self._day:
            return {}, {}
        return dict(self._visits), dict(self._spent)

    def visit(self, day: date, save_id: str, weight: int) -> None:
        if day != self._day:
            self._day, self._visits, self._spent = day, {}, {}
        self._visits[save_id] = weight

    def spend(self, day: date, save_id: str) -> None:
        if day == self._day:
            self._spent[save_id] = self._spent.get(save_id, 0) + 1
