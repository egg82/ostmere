"""Accounts on Postgres (interface.py). Each call that writes commits as it ends (db/unit.py); moving to another device
is moving.py. Making an account also deletes a small batch of empty accounts (no decision on any save) unused for
EMPTY_KEPT: the writer enforces its own retention, and an account with progress is never pruned. Recovery words and
codes go with their account."""

import logging
from datetime import timedelta

from sqlalchemy import Engine

from .. import logs
from ..clock import Clock
from ..db import accounts as rows
from ..db import reminders as reminder_rows
from ..db import unit
from ..db.accounts import SessionRecord
from . import limits, sessions
from .labels import UNKNOWN
from .interface import (About, Device, Joined, Json, Limited, NewAccount, NewCode, PresentationKept, Seen,
                        Subscription)
from .moving import Moving
from .presentation import merge_presentation

EMPTY_KEPT = timedelta(days=30)
PRUNE_BATCH = 20
WORDS_DUE_AFTER = timedelta(days=3)   # by then a player has a reason to keep the game

_log = logging.getLogger("ashfall.accounts")


class PgAccounts:
    def __init__(self, engine: Engine, clock: Clock, rate_key: bytes | None, join_key: bytes | None = None, *,
                 max_saves: int, moving: Moving | None = None) -> None:
        """`max_saves`: the most live saves an account holds (the Saves system's), which a merge must keep."""
        self._engine, self._clock, self._rate_key = engine, clock, rate_key
        self._moving = moving or Moving(engine, clock, rate_key, join_key, max_saves=max_saves)

    def who(self, token: str | None) -> Seen | None:
        if not token:
            return None
        with unit.read(self._engine) as conn:
            session = sessions.current(conn, token, self._clock())
        return None if session is None else Seen(session.account_id, session.id, session.last_seen_at)

    def renew(self, seen: Seen) -> bool:
        now = self._clock()
        if not sessions.due(seen.last_seen_at, now):
            return False
        with unit.begin(self._engine) as conn:
            return sessions.renew(conn, SessionRecord(seen.session_id, seen.account_id, seen.last_seen_at), now)

    def create(self, address: str, label: str | None = None) -> NewAccount:
        now = self._clock()
        scope = limits.refused(self._engine, self._rate_key, address, now)
        if scope is not None:
            raise Limited(scope)
        with unit.begin(self._engine) as conn:
            pruned = rows.delete_empty_accounts(conn, now - EMPTY_KEPT, PRUNE_BATCH)
            account_id = rows.create_account(conn, now)
            token = sessions.issue(conn, account_id, now, label)
        logs.info(_log, "account.created", account=account_id, pruned=pruned)
        return NewAccount(account_id=account_id, token=token)

    def about(self, account_id: int) -> About | None:
        with unit.read(self._engine) as conn:
            found = rows.account(conn, account_id)
        if found is None:
            return None
        due = found.has_progress and not found.has_words and found.created_at <= self._clock() - WORDS_DUE_AFTER
        return About(presentation=found.presentation, lessons=found.lessons, has_words=found.has_words, words_due=due)

    def keep_presentation(self, account_id: int, sent: Json, cap: int) -> PresentationKept | None:
        with unit.begin(self._engine) as conn:
            found = rows.keep_presentation(conn, account_id, lambda stored: merge_presentation(stored, sent, cap))
        return None if found is None else PresentationKept(before=found[0], after=found[1])

    def set_lessons(self, account_id: int, on: bool) -> bool:
        with unit.begin(self._engine) as conn:
            return rows.set_lessons(conn, account_id, on)

    def keep_save_presentation(self, account_id: int, save_id: int, sent: Json, cap: int) -> PresentationKept | None:
        with unit.begin(self._engine) as conn:
            found = rows.keep_save_presentation(conn, account_id, save_id,
                                                lambda stored: merge_presentation(stored, sent, cap))
        return None if found is None else PresentationKept(before=found[0], after=found[1])

    def make_code(self, account_id: int) -> NewCode | None:
        return self._moving.make_code(account_id)

    def make_words(self, account_id: int) -> str | None:
        return self._moving.make_words(account_id)

    def join(self, token: str | None, typed: str, merge: bool, address: str, label: str | None = None, *,
             keep: bool = False) -> Joined:
        return self._moving.join(token, typed, merge, address, label, keep=keep)

    def devices(self, account_id: int, session_id: int) -> list[Device]:
        with unit.read(self._engine) as conn:
            found = rows.sessions_of(conn, account_id)
        listed = [Device(d.session_id, d.label or UNKNOWN, d.created_at, d.last_seen_at, d.session_id == session_id)
                  for d in found]
        return sorted(listed, key=lambda d: not d.this_device)   # stable: this browser first

    def remove_device(self, account_id: int, session_id: int) -> bool:
        with unit.begin(self._engine) as conn:
            removed = rows.delete_session(conn, account_id, session_id)
        if removed:
            logs.info(_log, "device.removed", account=account_id, session=session_id)
        return removed

    def keep_reminder(self, account_id: int, sub: Subscription, window: reminder_rows.Window | None) -> reminder_rows.Window | None:
        now = self._clock()
        with unit.begin(self._engine) as conn:
            if window is None:
                kept = reminder_rows.refresh_device(conn, now, account_id, sub.endpoint, (sub.p256dh, sub.auth), sub.tz)
            else:
                kept = reminder_rows.keep_device(conn, now, reminder_rows.NewDevice(
                    account_id, sub.endpoint, sub.p256dh, sub.auth, window.after_hours, sub.tz, window.send_from_hour,
                    window.send_until_hour))
        logs.info(_log, "reminder.kept", account=account_id, picked=window is not None, on=kept is not None,
                  after_hours=None if kept is None else kept.after_hours)
        return None if kept is None else kept

    def drop_reminder(self, account_id: int, endpoint: str) -> bool:
        with unit.begin(self._engine) as conn:
            dropped = reminder_rows.delete_endpoint(conn, account_id, endpoint)
        logs.info(_log, "reminder.off", account=account_id, dropped=dropped)
        return dropped
