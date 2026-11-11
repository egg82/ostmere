"""Tester feedback on Postgres: the words a player sent from the page, kept for the owner to read back
(`python -m ashfall_app.feedback`, __main__.py). Each add counts against a limit in the tries table (accounts/limits.py
`check`, kind "feedback"): PER_WHO an hour from one client address and from one account, PER_PREFIX from one IPv6 /48,
and OVERALL an hour in all; a limit that cannot be counted refuses. An add also deletes a small batch of rows older than
KEPT, so the writer enforces its own retention. The text is stored and never logged: the line says who, which save and
how long."""

import logging
from datetime import timedelta

from sqlalchemy import Connection, Engine

from .. import logs
from ..accounts import limits
from ..accounts.interface import Limited
from ..clock import Clock
from ..db import feedback as rows
from ..db import saves, unit

KIND, KIND_PREFIX, KIND_ACCOUNT = "feedback", "feedback_prefix", "feedback_account"
PER_WHO = 5
PER_PREFIX = 15
OVERALL = 50
WINDOW = timedelta(hours=1)
KEPT = timedelta(days=180)
PRUNE_BATCH = 20

_log = logging.getLogger("ashfall.feedback")


def _table(account_id: int | None) -> tuple[limits.Limit, ...]:
    """Every client is counted by its address and /48; a browser with an account by that too."""
    by_account = () if account_id is None else (limits.Limit(KIND_ACCOUNT, PER_WHO, WINDOW, "account"),)
    return (limits.Limit(KIND, PER_WHO, WINDOW, "address"), limits.Limit(KIND_PREFIX, PER_PREFIX, WINDOW, "prefix"),
            *by_account, limits.Limit(KIND, OVERALL, WINDOW, "overall"))


class PgFeedback:
    def __init__(self, engine: Engine, clock: Clock, build: str, release: int, rate_key: bytes | None) -> None:
        self._engine, self._clock, self._build, self._release, self._key = engine, clock, build, release, rate_key

    def add(self, account_id: int | None, address: str, text: str, save_id: int | None) -> None:
        """Stores `text`. Its save is recorded only when `account_id` owns it. Limited past the limits."""
        now = self._clock()
        refused = limits.check(self._engine, self._key, address, _table(account_id), now,
                               None if account_id is None else f"account:{account_id}")
        if refused is not None:
            logs.warning(_log, "feedback.limited", scope=refused)
            raise Limited(refused)
        with unit.begin(self._engine) as conn:
            sent = self._sent(conn, account_id, save_id)
            rows.insert_feedback(conn, now, text, sent)
            pruned = rows.delete_before(conn, now - KEPT, PRUNE_BATCH)
        logs.info(_log, "feedback.received", account=account_id, save=sent.save_id, len=len(text), pruned=pruned)

    def _sent(self, conn: Connection, account_id: int | None, save_id: int | None) -> rows.Sent:
        found = None if account_id is None or save_id is None else saves.save(conn, save_id, account_id)
        last = [] if found is None else saves.last_lines(conn, found.id, 1)
        return rows.Sent(
            build=self._build, release=self._release, account_id=account_id, save_id=None if found is None else found.id,
            game_time=None if found is None else found.game_time, last_line=last[0].key if last else None)
