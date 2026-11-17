"""`python -m ashfall_app.jobs reminders`: send the reminders and hands-free notices that are due (reminders/run.py,
reminders/notices.py)."""

import logging
import os
import sys
from collections.abc import Callable, Mapping

from sqlalchemy import Engine

from .. import clock, logs
from ..db.engine import open_database
from ..db.handsfree import Latest
from ..opening.lock import load_lock
from ..opening.renames import load_renames
from ..opening.schema import load_opening
from ..reminders.config import load_config, min_busy_s
from ..reminders.notices import run_notices
from ..reminders.run import run
from ..reminders.sender import WebPushSender
from ..saves import handsfree
from ..saves.interface import Ruleset
from ..saves.ruleset import ruleset
from ..saves.service import wall_budget

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
        sender = WebPushSender(cfg)
        run(database.engine, sender, clock.system)
        run_notices(database.engine, sender, clock.system, refresher(database.engine, env.get("BUILD_VERSION", "dev")))
    finally:
        database.close()
    return 0


def refresher(engine: Engine, build: str) -> Callable[[Latest], bool]:
    """The refresh of one save's hands-free answer, under the rules this image ships, read at the first save that
    needs one: most runs need none, and reading the content takes a while."""
    held: list[Ruleset] = []

    def refresh(latest: Latest) -> bool:
        if not held:
            held.append(ruleset(load_opening(), load_renames(), build, load_lock().release))
        return handsfree.refresh(engine, held[0], latest, min_busy_s(), wall_budget())
    return refresh
