"""One pass of the hands-free notice (docs/design/reminders.md, "The hands-free notice"), run by the reminders job: each
account that takes it has its latest save read; one whose kept forecast has run out is forecast afresh (`refresh`, the
Saves system's); one whose notice is due and has a device inside its notification times is claimed, then sent to
those devices; with none inside, it waits for a later run, unclaimed. Every number of the pass is on its last line."""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Engine

from .. import logs
from ..clock import Clock
from ..db import handsfree as saves
from ..db import reminders as store
from .deliver import deliver
from .due import notice_due, open_now
from .sender import Sender
from .words import notice_payload

log = logging.getLogger("ashfall.reminders")


@dataclass(frozen=True)
class NoticeCounts:
    saves: int = 0
    refreshed: int = 0
    unrefreshed: int = 0
    due: int = 0
    sent: int = 0
    gone: int = 0
    failed: int = 0


def run_notices(engine: Engine, sender: Sender, clock: Clock, refresh: Callable[[saves.Latest], bool]) -> NoticeCounts:
    started, now = time.perf_counter(), clock()
    with engine.connect() as conn:
        found = saves.latest(conn)
    stale = [s for s in found if s.stale(now)]
    refreshed = sum(_refreshed(refresh, s) for s in stale)
    if refreshed:
        with engine.connect() as conn:
            found = saves.latest(conn)
    ready = [s for s in found if notice_due(s.at, s.wall, s.game_time, s.sent, now)]
    went: list[str] = []
    for s in ready:
        assert s.at is not None
        with engine.connect() as conn:
            takers = store.notice_targets(conn, s.account_id)
        targets = [d.target for d in takers if open_now(now, d.tz, d.send_from_hour, d.send_until_hour)]
        if not targets:
            continue
        with engine.begin() as conn:
            claimed = saves.claim(conn, s.save_id, s.at)
        if not claimed:
            continue
        went += [deliver(engine, sender, t, notice_payload(s.account_id, s.at), "notice") for t in targets]
    counts = NoticeCounts(len(found), refreshed, len(stale) - refreshed, len(ready), went.count("ok"),
                          went.count("gone"), went.count("error"))
    logs.info(log, "hands_free.run", saves=counts.saves, refreshed=refreshed, unrefreshed=counts.unrefreshed,
              due=counts.due, sent=counts.sent, gone=counts.gone, failed=counts.failed,
              ms=int((time.perf_counter() - started) * 1000))
    return counts


def _refreshed(refresh: Callable[[saves.Latest], bool], s: saves.Latest) -> bool:
    """One save's refresh; one that raises is logged by the type of what it raised and counted as not refreshed, so
    the other saves still get theirs."""
    try:
        return refresh(s)
    except Exception as ex:
        logs.warning(log, "hands_free.refresh_failed", save=s.save_id, why=type(ex).__name__)
        return False
