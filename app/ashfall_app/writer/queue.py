"""The writer's queue: jobs for worlds whose player came back today, run against the daily budget. A job the budget
cannot cover is answered with its stand-in, so the player never sees a cap."""

import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from .. import logs
from . import budget as budgets
from .service import Writer

log = logging.getLogger("ashfall.writer")


@dataclass(frozen=True)
class Job:
    save_id: str
    kind: str
    stand_in: str


class Queue:
    """Counts live in memory and reset with the day; a restart forgets them (persistence lands with the live client)."""

    def __init__(self, writer: Writer, today: Callable[[], date], budget: budgets.Budget = budgets.DEFAULT) -> None:
        self.writer = writer
        self.today = today
        self.budget = budget
        self._pending: deque[Job] = deque()
        self._day = today()
        self._visits: dict[str, int] = {}
        self._spent: dict[str, int] = {}

    def visit(self, save_id: str, returning_days: int) -> None:
        """The save's player came back today, `returning_days` days they have come back before."""
        self._roll()
        self._visits[save_id] = budgets.weight(self.budget, returning_days)

    def enqueue(self, job: Job) -> bool:
        """False, and nothing queued, for a save whose player has not come back today."""
        self._roll()
        if job.save_id not in self._visits:
            self._log("skip", job, "abandoned")
            return False
        self._pending.append(job)
        return True

    def drain(self) -> list[tuple[Job, str]]:
        """Run every queued job, oldest first: the written text, or the stand-in when over a cap."""
        out: list[tuple[Job, str]] = []
        while self._pending:
            job = self._pending.popleft()
            self._roll()
            reason = self._over(job)
            if reason:
                self._log("skip", job, reason)
                out.append((job, job.stand_in))
                continue
            self._spent[job.save_id] = self._spent.get(job.save_id, 0) + 1
            text = self.writer.write(job.kind, job.stand_in)
            self._log("run", job, "ok")
            out.append((job, text))
        return out

    def _over(self, job: Job) -> str | None:
        if sum(self._spent.values()) >= self.budget.global_daily:
            return "global_cap"
        weights = list(self._visits.values())
        own = self._visits.get(job.save_id)
        if own is None:
            return "abandoned"
        if self._spent.get(job.save_id, 0) >= budgets.allowance(self.budget, own, weights):
            return "save_cap"
        return None

    def _roll(self) -> None:
        if self.today() != self._day:
            self._day = self.today()
            self._visits, self._spent = {}, {}

    def _log(self, event: str, job: Job, reason: str) -> None:
        logs.info(log, f"writer.job.{event}", kind=job.kind, save=logs.tag(job.save_id), reason=reason,
                  save_spent=self._spent.get(job.save_id, 0), global_spent=sum(self._spent.values()),
                  worlds=len(self._visits), pending=len(self._pending))
