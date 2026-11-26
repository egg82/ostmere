"""`python -m ashfall_app.jobs reminders`, each minute: send the reminders and hands-free notices that are due
(reminders/run.py, reminders/notices.py), then keep the catch-up of saves whose players are away ahead of their clocks
(saves/ahead.py)."""

import logging
import os
import sys
from collections.abc import Callable, Mapping

from sqlalchemy import Engine

from .. import clock, logs
from ..db.engine import open_database
from ..db.handsfree import Latest
from ..opening.schema import load_opening
from ..reminders.config import load_config, min_busy_s
from ..reminders.notices import run_notices
from ..reminders.run import run
from ..reminders.sender import WebPushSender
from ..saves import ahead, handsfree
from ..saves.interface import Ruleset
from ..saves.ruleset import build_release, ruleset
from ..saves.service import wall_budget

log = logging.getLogger("ashfall.reminders")


AHEAD_RUN_S = 40.0
"""Wall seconds a run spends keeping saves ahead, after the reminders, so the next minute's run starts on time."""


def main(env: Mapping[str, str] = os.environ) -> int:
    """0 when the run finished, or there are neither VAPID keys nor a database to run with; 2 when VAPID keys are set
    and DATABASE_URL is missing; a failed run raises, which the CronJob shows as a failed pod."""
    cfg = load_config(env)
    if cfg is None:
        logs.info(log, "reminders.skip", why="no_vapid_config")
    url = env.get("DATABASE_URL", "")
    if not url:
        if cfg is None:
            return 0
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2
    database = open_database(url)
    rules = shipped(env.get("BUILD_VERSION", "dev"))
    try:
        if cfg is not None:
            sender = WebPushSender(cfg)
            run(database.engine, sender, clock.system)
            run_notices(database.engine, sender, clock.system, refresher(database.engine, rules))
        ahead.keep(database.engine, rules, clock.system, AHEAD_RUN_S)
    finally:
        database.close()
    return 0


def shipped(build: str) -> Callable[[], Ruleset]:
    """The rules this image ships, read when first asked for: most runs need none, and reading the content takes a
    while."""
    held: list[Ruleset] = []

    def rules() -> Ruleset:
        if not held:
            held.append(ruleset(load_opening(), build, build_release()))
        return held[0]
    return rules


def refresher(engine: Engine, rules: Callable[[], Ruleset]) -> Callable[[Latest], bool]:
    """The refresh of one save's hands-free answer, under the rules this image ships."""
    def refresh(latest: Latest) -> bool:
        return handsfree.refresh(engine, rules(), latest, min_busy_s(), wall_budget())
    return refresh
