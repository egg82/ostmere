"""A join, inside one transaction (api/CONTRACT.txt, "Moving to another device"). T is the account the code or words
name, D the account of this browser's live session. Both rows are held, lowest id first, before anything is decided,
and D's saves are held while its progress is read, so a decision landing meanwhile is seen and a new game on either
waits. The rows are db/joins.py; a code is used up only by a join that goes through. A merge moves only D's own saves,
D being the account of the session that asked, into T, never the other way. A join that keeps leaves D, its saves and
its other sessions as they were and moves only the asking session; D's recovery words are made there when it has none,
since this browser can no longer ask for them."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import Connection

from ..db import accounts as rows
from ..db import codes as code_rows
from ..db import joins
from ..db.joins import Holds
from . import sessions

type Via = Literal["code", "words"]


@dataclass(frozen=True)
class Outcome:
    kind: Literal["joined", "nothing", "confirm", "full", "moving", "clash"]
    """moving: this browser's session changed hands while the join waited; nothing changed, try again. clash: the
    words offered for D match another account's; nothing changed, offer others."""
    there: int | None = None
    here: int | None = None
    """D, when the browser had a live session."""
    token: str | None = None
    """A new session of T, for a browser that had none."""
    sessions_moved: int = 0
    moved: int = 0
    """D's saves that became T's."""
    holds: Holds | None = None
    kept: int | None = None
    """D's live saves left on D by a join that keeps; None for any other join."""
    words_set: bool = False
    """D had no recovery words and now has the ones offered."""


NOTHING = Outcome("nothing")


def join(conn: Connection, token: str | None, via: Via, secret: bytes, now: datetime, merge: bool,
         max_saves: int, label: str | None, keep_words: bytes | None = None) -> Outcome:
    """`keep_words`: the hashed words offered for D when this browser leaves its games on D (None: it does not)."""
    there = code_rows.holder(conn, secret, now) if via == "code" else rows.account_by_words(conn, secret)
    if there is None:
        return NOTHING
    first = sessions.current(conn, token, now)
    held = joins.lock_accounts(conn, {there} if first is None else {there, first.account_id})
    if there not in held:
        return NOTHING
    if first is None:
        return _used(conn, via, secret, Outcome("joined", there=there, token=sessions.issue(conn, there, now, label)))
    session = sessions.current(conn, token, now)
    if session is None or session.account_id != first.account_id:
        return Outcome("moving")
    here = session.account_id
    if here == there:
        return _used(conn, via, secret, Outcome("joined", there=there, here=here))
    saves_moved = 0
    if joins.has_progress(conn, here):
        holds = joins.holds(conn, here, there)
        if keep_words is not None:
            kept = _kept(conn, session.id, Ends(here, there), holds.here, keep_words, now)
            return kept if kept.kind == "clash" else _used(conn, via, secret, kept)
        if holds.here + holds.there > max_saves:
            return Outcome("full", there=there, here=here, holds=holds)
        if not merge:
            return Outcome("confirm", there=there, here=here, holds=holds)
        saves_moved = joins.move_saves(conn, here, there)
    moved = joins.move_sessions(conn, here, there)
    joins.move_reminders(conn, here, there)
    rows.keep_newest_sessions(conn, there, sessions.PER_ACCOUNT)
    joins.carry_words(conn, here, there)
    joins.delete_empty_account(conn, here)
    return _used(conn, via, secret, Outcome("joined", there=there, here=here, sessions_moved=moved, moved=saves_moved))


@dataclass(frozen=True)
class Ends:
    here: int
    there: int


def _kept(conn: Connection, session_id: int, ends: Ends, live: int, words: bytes, now: datetime) -> Outcome:
    """This session alone becomes T's; D keeps everything, and its words when it has them."""
    found = rows.account(conn, ends.here)
    worded = found is not None and not found.has_words
    if worded and rows.set_words(conn, ends.here, words, now) is None:
        return Outcome("clash")
    joins.move_session(conn, session_id, ends.there)
    rows.keep_newest_sessions(conn, ends.there, sessions.PER_ACCOUNT)
    return Outcome("joined", there=ends.there, here=ends.here, kept=live, words_set=worded)


def _used(conn: Connection, via: Via, secret: bytes, outcome: Outcome) -> Outcome:
    if via == "code":
        code_rows.use(conn, secret)
    return outcome
