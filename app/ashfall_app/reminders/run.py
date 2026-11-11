"""One run of the reminders job: find the devices due, claim each before sending to it, send, prune. Every number of
the run is on its last line."""

import logging
import time
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import Engine

from .. import logs
from ..clock import Clock
from ..db import reminders as store
from .due import due
from .sender import Sender
from .words import payload

log = logging.getLogger("ashfall.reminders")

RETENTION = timedelta(days=180)
"""A device whose player has not visited for this long is deleted."""
PRUNE_BATCH = 1000


@dataclass(frozen=True)
class Counts:
    due: int = 0
    sent: int = 0
    gone: int = 0
    failed: int = 0
    pruned: int = 0


def run(engine: Engine, sender: Sender, clock: Clock) -> Counts:
    started = time.perf_counter()
    logs.info(log, "reminders.start")
    now = clock()
    with engine.connect() as conn:
        candidates = store.unsent(conn)
    ready = [d for d in candidates if due(
        d.visited_at, timedelta(hours=d.after_hours), d.last_sent_at, now, d.tz, d.send_from_hour, d.send_until_hour)]
    sent = gone = failed = 0
    for d in ready:
        with engine.begin() as conn:
            claimed = store.claim(conn, d.id, d.visited_at, now)
        if not claimed:
            continue
        delivery = sender.send(d.endpoint, d.p256dh, d.auth, payload(d.account_id, d.visited_at))
        if delivery.kind == "ok":
            sent += 1
        elif delivery.kind == "gone":
            gone += 1
            logs.info(log, "reminders.gone", device=d.id, status=delivery.status)
            with engine.begin() as conn:
                store.delete_device(conn, d.id)
        else:
            failed += 1
            logs.warning(log, "reminders.send_failed", device=d.id, status=delivery.status, why=delivery.why)
    with engine.begin() as conn:
        pruned = store.delete_unvisited_before(conn, now - RETENTION, PRUNE_BATCH)
    counts = Counts(len(ready), sent, gone, failed, pruned)
    logs.info(log, "reminders.run", due=counts.due, sent=sent, gone=gone, failed=failed, pruned=pruned,
              ms=int((time.perf_counter() - started) * 1000))
    return counts
