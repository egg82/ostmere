"""`python -m ashfall_app.jobs reminders`: send the reminders that are due (reminders/run.py)."""

import logging
import os
import sys
from collections.abc import Mapping

from .. import clock, logs
from ..db.engine import open_database
from ..reminders.config import load_config
from ..reminders.run import run
from ..reminders.sender import WebPushSender

log = logging.getLogger("ashfall.reminders")


def main(env: Mapping[str, str] = os.environ) -> int:
    """0 when the run finished or there are no VAPID keys to run with; 2 when DATABASE_URL is missing; a failed run
    raises, which the CronJob shows as a failed pod."""
    cfg = load_config(env)
    if cfg is None:
        logs.info(log, "reminders.skip", why="no_vapid_config")
        return 0
    url = env.get("DATABASE_URL", "")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2
    database = open_database(url)
    try:
        run(database.engine, WebPushSender(cfg), clock.system)
    finally:
        database.close()
    return 0
