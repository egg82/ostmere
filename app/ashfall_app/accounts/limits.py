"""The limits of api/CONTRACT.txt (429 rate_limited): on making accounts, PER_ADDRESS from one client address and
OVERALL in all, per WINDOW; and on moving to another device, joins per client address, joins that found nothing across
everyone, and codes and words made per account; new games per account, and decisions per save (saves/). Each is a Limit: at most `n` tries of `kind` within `window`, counted
per `who` (a client, an IPv6 client's /48 prefix, an account, or all). Counted in the tries table, so every pod shares one count and a deploy
forgets nothing; one row per try let through (and per join that found nothing), each kind trimmed past its window on
every insert. A client is keyed by HMAC-SHA256(ASHFALL_RATE_KEY, address), never the address. A count and the insert
that follows it run under one lock per kind across pods (db/tries.py `hold`).
`check` is the same count for any table of Limits (feedback/ has its own).

Fails closed: no key, or a database error, refuses; a failover error is raised instead (db/failover.py)."""

import hashlib
import hmac
import ipaddress
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import Connection, Engine

from .. import logs
from ..db import failover, tries, unit

KIND, KIND_PREFIX = "account", "account_prefix"
PER_ADDRESS = 10
PER_PREFIX = 30
OVERALL = 200
WINDOW = timedelta(hours=1)
JOIN, JOIN_PREFIX, JOIN_PER_ADDRESS, JOIN_PER_PREFIX, JOIN_WINDOW = "join", "join_prefix", 10, 30, timedelta(minutes=15)
JOIN_FAIL, JOIN_FAILS, JOIN_FAIL_WINDOW = "join_fail", 300, timedelta(hours=1)
CODE_MAKE, CODES, CODE_WINDOW = "code_make", 10, timedelta(hours=1)
WORDS_MAKE, WORDS, WORDS_WINDOW = "words_make", 5, timedelta(hours=24)
NEW_GAME, NEW_GAMES, NEW_GAME_WINDOW = "new_game", 10, timedelta(hours=24)
DECISION = "decision"
DECISIONS_PER_MINUTE, DECISIONS_MINUTE = 120, timedelta(minutes=1)
DECISIONS_PER_HOUR, DECISIONS_HOUR = 3600, timedelta(hours=1)
"""Decisions one save may take, each one a stored row. The fastest play that writes rows is repeated taps on the
shortest hands card (3 s, a tap on a busy lane writes nothing): 20 a minute, 1,200 an hour; an editor saves a handful at
once, and the scripted opening player (faster than a hand) peaks at 10 a minute. Both limits are three to six times the
tapping, so play never meets them."""
"""An IPv6 client is counted by its /64, so one holder of a /48 has 65,536 of them and could reach OVERALL or JOIN_FAILS
alone, locking everyone out. PER_PREFIX and JOIN_PER_PREFIX count the /48 too, at three times a /64's allowance (a /48 is
a site or a few households, each with at least one /64): a prefix meets its own limit first. 30 an hour is under a sixth of
OVERALL; 30 joins in 15 minutes is at most 120 an hour, under JOIN_FAILS' 300. IPv4 has no prefix limit."""
EVERYONE = b"all"   # the `who` of a count across every client
UNCOUNTED_RETRY_S = 60   # Retry-After when a limit could not be counted

_log = logging.getLogger("ashfall.accounts")


@dataclass(frozen=True)
class Limit:
    kind: str
    n: int
    window: timedelta
    who: Literal["address", "prefix", "account", "save", "overall"]   # also the scope a refusal reports


@dataclass(frozen=True)
class Refusal:
    scope: str
    """address, account, overall, no_key or error (made() reports code_make, words_make or new_game for an
    account's)."""
    retry_after_s: int


def _table() -> tuple[Limit, ...]:
    return (Limit(KIND, PER_ADDRESS, WINDOW, "address"), Limit(KIND_PREFIX, PER_PREFIX, WINDOW, "prefix"),
            Limit(KIND, OVERALL, WINDOW, "overall"))


def _made(kind: str) -> Limit:
    return {CODE_MAKE: Limit(CODE_MAKE, CODES, CODE_WINDOW, "account"),
            WORDS_MAKE: Limit(WORDS_MAKE, WORDS, WORDS_WINDOW, "account"),
            NEW_GAME: Limit(NEW_GAME, NEW_GAMES, NEW_GAME_WINDOW, "account")}[kind]


def _decisions() -> tuple[Limit, ...]:
    return (Limit(DECISION, DECISIONS_PER_MINUTE, DECISIONS_MINUTE, "save"),
            Limit(DECISION, DECISIONS_PER_HOUR, DECISIONS_HOUR, "save"))


def client_key(key: bytes, address: str) -> bytes:
    """The keyed hash a client is counted under: an IPv6 address by its /64 (one household holds a whole /64, so
    per-address would be no limit), an IPv4-mapped one as the IPv4 address, anything unparseable as it came."""
    return hmac.new(key, _client(address).encode(), hashlib.sha256).digest()


def prefix_key(key: bytes, address: str) -> bytes | None:
    """The keyed hash of an IPv6 client's /48; None for IPv4, an IPv4-mapped address or anything unparseable."""
    ip = _ip(address)
    if not isinstance(ip, ipaddress.IPv6Address) or ip.ipv4_mapped is not None:
        return None
    return hmac.new(key, str(ipaddress.ip_network((ip, 48), strict=False)).encode(), hashlib.sha256).digest()


def _ip(address: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(address)
    except ValueError:
        return None


def _client(address: str) -> str:
    ip = _ip(address)
    if ip is None:
        return address
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return str(ip.ipv4_mapped)
        return str(ipaddress.ip_network((ip, 64), strict=False))
    return str(ip)


def refused(engine: Engine, key: bytes | None, address: str, now: datetime) -> str | None:
    """Counts one new account from `address`, unless a limit is reached: None when it may go ahead, else the scope
    that refused it (address, overall, no_key, error), logged as account.limited."""
    scope = check(engine, key, address, _table(), now)
    if scope is not None:
        logs.warning(_log, "account.limited", scope=scope)
    return scope


def check(engine: Engine, key: bytes | None, subject: str, table: tuple[Limit, ...], now: datetime,
          account: str | None = None) -> str | None:
    """Counts one try by `subject` (an address, or any string naming who is counted) against `table`: None when it may
    go ahead, else the scope that refused it (a Limit's, no_key, error). With `account`, the table's "account" limits
    count it, under their own kinds, beside the subject's."""
    if not key:
        return "no_key"
    who = client_key(key, subject)
    kind = table[0].kind   # the kind whose lock serialises the table
    try:
        with unit.begin(engine) as conn:
            found = _take(conn, kind, who, table, now, prefix=prefix_key(key, subject),
                          account=None if account is None else client_key(key, account))
        return None if found is None else found.scope
    except Exception as ex:
        failover.let_through(ex)
        _log.error("account.limit_error", extra={"fields": {"kind": kind}}, exc_info=True)   # the type chain, never a message
        return "error"


def _take(conn: Connection, kind: str, who: bytes, table: tuple[Limit, ...], now: datetime,
          prefix: bytes | None = None, account: bytes | None = None) -> Refusal | None:
    """Counts one try of `kind` by `who` unless a limit of `table` is reached: then the refusal, counting nothing.
    A "prefix" limit counts `prefix` under its own kind (the kind's lock serialises it too) and is skipped without one.
    An "account" limit counts `account` the same way, or `who` when there is none."""
    tries.hold(conn, kind)
    for k in {limit.kind for limit in table}:
        tries.trim(conn, k, now - max(limit.window for limit in table if limit.kind == k))
    for limit in table:
        if limit.who == "prefix" and prefix is None:
            continue
        found = _reached(conn, limit, _counted(limit, who, prefix, account), now)
        if found is not None:
            return found
    tries.add(conn, kind, who, now)
    for limit in table:
        if limit.who == "prefix" and prefix is not None:
            tries.add(conn, limit.kind, prefix, now)
        elif limit.who == "account" and account is not None:
            tries.add(conn, limit.kind, account, now)
    return None


def _counted(limit: Limit, who: bytes, prefix: bytes | None, account: bytes | None) -> bytes | None:
    """Whose tries `limit` counts: None for everyone's."""
    if limit.who == "overall":
        return None
    if limit.who == "prefix":
        return prefix
    return account if limit.who == "account" and account is not None else who


def _reached(conn: Connection, limit: Limit, who: bytes | None, now: datetime) -> Refusal | None:
    since = now - limit.window
    if tries.count(conn, limit.kind, since, who) < limit.n:
        return None
    oldest = tries.oldest(conn, limit.kind, since, who) or now
    return Refusal(limit.who, _wait(limit, oldest, now))


def _wait(limit: Limit, oldest: datetime, now: datetime) -> int:
    """Whole seconds, at least one, until `oldest` leaves the limit's window."""
    return max(1, math.ceil((oldest + limit.window - now).total_seconds()))


def join_try(engine: Engine, key: bytes | None, address: str, now: datetime) -> Refusal | None:
    """Counts one join from `address`, unless its address is past JOIN_PER_ADDRESS, its /48 past JOIN_PER_PREFIX or the
    joins that found nothing are past JOIN_FAILS: None when it may go ahead, else the refusal."""
    if not key:
        return Refusal("no_key", UNCOUNTED_RETRY_S)
    fails = Limit(JOIN_FAIL, JOIN_FAILS, JOIN_FAIL_WINDOW, "overall")
    per_address = Limit(JOIN, JOIN_PER_ADDRESS, JOIN_WINDOW, "address")
    per_prefix = Limit(JOIN_PREFIX, JOIN_PER_PREFIX, JOIN_WINDOW, "prefix")
    try:
        with unit.begin(engine) as conn:
            return _reached(conn, fails, None, now) or _take(
                conn, JOIN, client_key(key, address), (per_address, per_prefix), now, prefix=prefix_key(key, address))
    except Exception as ex:
        failover.let_through(ex)
        _log.error("join.limit_error", extra={"fields": {}}, exc_info=True)
        return Refusal("error", UNCOUNTED_RETRY_S)


def found_nothing(engine: Engine, now: datetime) -> None:
    """Counts a join whose code or words found nothing, against JOIN_FAILS. A count that fails is logged, not raised:
    the join is refused either way."""
    try:
        with unit.begin(engine) as conn:
            tries.hold(conn, JOIN_FAIL)
            tries.trim(conn, JOIN_FAIL, now - JOIN_FAIL_WINDOW)
            tries.add(conn, JOIN_FAIL, EVERYONE, now)
    except Exception:
        _log.error("join.limit_error", extra={"fields": {}}, exc_info=True)


def made(engine: Engine, kind: str, account_id: int, now: datetime) -> Refusal | None:
    """Counts one code (CODE_MAKE) or set of words (WORDS_MAKE) made for the account, unless its limit is reached."""
    try:
        with unit.begin(engine) as conn:
            return made_in(conn, kind, account_id, now)
    except Exception as ex:
        failover.let_through(ex)
        _log.error("join.limit_error", extra={"fields": {}}, exc_info=True)
        return Refusal("error", UNCOUNTED_RETRY_S)


def made_in(conn: Connection, kind: str, account_id: int, now: datetime) -> Refusal | None:
    """made() in the caller's transaction, so the count and what it lets through are one step (a new game, NEW_GAME,
    counted while the account's row is held). A database error is raised, and the caller refuses."""
    found = _take(conn, kind, str(account_id).encode(), (_made(kind),), now)
    return None if found is None else Refusal(kind, found.retry_after_s)


def decided_in(conn: Connection, save_id: int, now: datetime) -> Refusal | None:
    """Counts one decision on the save, in the caller's transaction, which holds the save's row: that serialises the
    save's count, so the kind is not locked and decisions on different saves never wait on each other. A decision
    that then fails rolls its count back with it."""
    table = _decisions()
    readings = tries.take(conn, DECISION, str(save_id).encode(), [(limit.n, limit.window) for limit in table], now)
    for limit, found in zip(table, readings, strict=True):
        if found.found >= limit.n:
            return Refusal(DECISION, _wait(limit, found.oldest or now, now))
    return None
