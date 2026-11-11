"""Moving an account to another device, on Postgres (PgAccounts hands these calls here): transfer codes, recovery words
and the join either one makes. The limits come first (limits.py), then the hash (outside any transaction: words take
scrypt's time), then one transaction (join.py). Without ASHFALL_JOIN_KEY every call is refused (AccountsUnavailable).

Logs carry ids, counts and kinds; never a code, words, a hash, a token or an address."""

import logging
import time
from datetime import datetime

from sqlalchemy import Connection, Engine

from .. import logs
from ..clock import Clock
from ..db import accounts as rows
from ..db import codes as code_rows
from ..db import unit
from . import codes, join as joining, limits, words
from .interface import (AccountsUnavailable, ConfirmMerge, Joined, Kept, Limited, MergeFull, MergeSummary, NewCode,
                        NoSuchCode)

_log = logging.getLogger("ashfall.accounts")


class Moving:
    def __init__(self, engine: Engine, clock: Clock, rate_key: bytes | None, join_key: bytes | None, *, max_saves: int,
                 hashing: words.Hashing | None = None) -> None:
        self._engine, self._clock, self._rate_key, self._join_key = engine, clock, rate_key, join_key
        self._max_saves = max_saves
        self._hashing = hashing or words.Hashing()

    def _key(self) -> bytes:
        if not self._join_key:
            raise AccountsUnavailable("no join key")
        return self._join_key

    def make_code(self, account_id: int) -> NewCode | None:
        key, now = self._key(), self._clock()
        _limited(limits.made(self._engine, limits.CODE_MAKE, account_id, now))
        with unit.begin(self._engine) as conn:
            if not rows.lock_account(conn, account_id):
                return None
            replaced = code_rows.delete_codes_of(conn, account_id)
            swept = code_rows.delete_expired(conn, now, codes.SWEEP)
            code = _store_code(conn, key, account_id, now)
        expires_s = int(codes.LIFETIME.total_seconds())
        logs.info(_log, "transfer.made", account=account_id, expires_s=expires_s, replaced=replaced, swept=swept)
        return NewCode(code=codes.shown(code), expires_in_s=expires_s)

    def make_words(self, account_id: int) -> str | None:
        key, now = self._key(), self._clock()
        _limited(limits.made(self._engine, limits.WORDS_MAKE, account_id, now))
        for _ in range(codes.TRIES):
            made = words.make()
            hashed = self._digest(key, made)
            with unit.begin(self._engine) as conn:
                before = rows.account(conn, account_id)
                done = None if before is None else rows.set_words(conn, account_id, hashed, now)
            if before is None or done is False:
                return None
            if done:
                logs.info(_log, "words.made", account=account_id, replaced=before.has_words)
                return made
        raise RuntimeError("recovery words kept matching another account's")

    def join(self, token: str | None, typed: str, merge: bool, address: str, label: str | None = None, *,
             keep: bool = False) -> Joined:
        started = time.perf_counter()
        key, now = self._key(), self._clock()
        refusal = limits.join_try(self._engine, self._rate_key, address, now)
        if refusal is not None:
            logs.warning(_log, "join.limited", scope=refusal.scope)
            raise Limited(refusal.scope, refusal.retry_after_s)
        code, said = codes.normal(typed), words.normal(typed)
        if code is None and said is None:
            logs.info(_log, "join.refused", reason="not_a_code")
            raise NoSuchCode()
        via: joining.Via = "code" if code is not None else "words"
        secret = codes.digest(key, code) if code is not None else self._digest(key, said or "")
        for _ in range(codes.TRIES):
            offered = words.make() if keep else None
            hashed = None if offered is None else self._digest(key, offered)
            with unit.begin(self._engine) as conn:
                outcome = joining.join(conn, token, via, secret, now, merge, self._max_saves, label, hashed)
            if outcome.kind != "clash":
                return _answer(self._engine, outcome, via, now, started, self._max_saves, offered)
        raise RuntimeError("recovery words kept matching another account's")

    def _digest(self, key: bytes, said: str) -> bytes:
        try:
            return self._hashing.digest(key, said)
        except words.Busy as ex:
            logs.warning(_log, "join.limited", scope="busy")
            raise Limited("busy", words.BUSY_RETRY_S) from ex


def _limited(refusal: limits.Refusal | None) -> None:
    if refusal is not None:
        logs.warning(_log, "join.limited", scope=refusal.scope)
        raise Limited(refusal.scope, refusal.retry_after_s)


def _store_code(conn: Connection, key: bytes, account_id: int, now: datetime) -> str:
    for _ in range(codes.TRIES):
        code = codes.make()
        if code_rows.insert_code(conn, account_id, codes.digest(key, code), now, now + codes.LIFETIME):
            return code
    raise RuntimeError("transfer codes kept matching stored ones")


def _answer(engine: Engine, outcome: joining.Outcome, via: joining.Via, now: datetime, started: float,
            max_saves: int, offered: str | None) -> Joined:
    if outcome.kind == "nothing":
        limits.found_nothing(engine, now)
        logs.info(_log, "join.refused", reason="no_such_code", via=via)
        raise NoSuchCode()
    if outcome.kind == "moving":
        logs.info(_log, "join.refused", reason="session_moved", via=via)
        raise AccountsUnavailable("this browser's session moved while joining: try again")
    if outcome.kind in ("confirm", "full") and outcome.holds is not None:
        h = outcome.holds
        reason = "confirm_needed" if outcome.kind == "confirm" else "full"
        logs.info(_log, "join.refused", reason=reason, via=via, account=outcome.there, here=outcome.here,
                  saves_here=h.here, saves_there=h.there)
        summary = MergeSummary(here=h.here, there=h.there, there_newest_game_time=h.there_newest_game_time,
                               max_saves=max_saves, words_replaced=h.words_replaced)
        raise ConfirmMerge(summary) if outcome.kind == "confirm" else MergeFull(summary)
    assert outcome.there is not None
    logs.info(_log, "join.ok", account=outcome.there, via=via, **{"from": outcome.here}, moved=outcome.moved,
              sessions_moved=outcome.sessions_moved, kept=outcome.kept, words_set=outcome.words_set,
              ms=int((time.perf_counter() - started) * 1000))
    kept = None if outcome.kept is None else Kept(outcome.kept, offered if outcome.words_set else None)
    return Joined(account_id=outcome.there, moved=outcome.moved, token=outcome.token, kept=kept)
