"""Sessions: a random token in a cookie, stored only as its sha256, kept alive by use (habits' signin/sessions.py,
without its sign-in ways). A session used within LIFETIME stays good, and each day it is used its last use is stored
and its cookie set again, so a browser that plays now and then never loses its account. An account keeps at most
PER_ACCOUNT sessions: making one more drops the longest unused. A token is never rotated (two tabs would race it).
These run in the caller's transaction."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta

from sqlalchemy import Connection

from .. import logs
from ..db import accounts as rows
from ..db.accounts import SessionRecord

LIFETIME = timedelta(days=400)   # Chrome's longest cookie
RENEW = timedelta(days=1)
PER_ACCOUNT = 20

_log = logging.getLogger("ashfall.accounts")


def token_hash(token: str) -> bytes:
    return hashlib.sha256(token.encode()).digest()


def current(conn: Connection, token: str | None, now: datetime) -> SessionRecord | None:
    """The session `token` names, if it is still alive."""
    if not token:
        return None
    return rows.session_by_hash(conn, token_hash(token), now - LIFETIME)


def due(last_seen_at: datetime, now: datetime) -> bool:
    """A session last used at `last_seen_at` is marked used again."""
    return now - last_seen_at >= RENEW


def renew(conn: Connection, session: SessionRecord, now: datetime) -> bool:
    """Marks the session and its account used, at most once a day; True when it did (set the cookie again)."""
    if not due(session.last_seen_at, now):
        return False
    rows.touch(conn, session, now)
    logs.info(_log, "session.renewed", account=session.account_id, session=session.id)
    return True


def issue(conn: Connection, account_id: int, now: datetime, label: str | None = None) -> str:
    """A new session for the account, with its device label (labels.py); its token, for the cookie. Drops the
    account's longest unused past PER_ACCOUNT, and every session unused for LIFETIME."""
    token = secrets.token_urlsafe(32)
    rows.insert_session(conn, account_id, token_hash(token), now, label)
    rows.keep_newest_sessions(conn, account_id, PER_ACCOUNT)
    rows.delete_sessions_unused_since(conn, now - LIFETIME)
    return token
