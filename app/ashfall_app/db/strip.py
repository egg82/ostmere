"""The rows the strip backfill (saves/strip.py) reads and writes: save and snapshot states that still carry their own
manifest, read a batch at a time in key order; each written back stripped only while it is still the text read; and
the manifests no row names."""

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import ColumnElement, Connection, Table, and_, delete, exists, func, literal, not_, select, tuple_, update

from .manifests import carries_own
from .tables import save_manifests, save_snapshots, saves

type Kind = Literal["saves", "snapshots"]
KINDS: tuple[Kind, ...] = ("saves", "snapshots")
_TABLES: dict[Kind, Table] = {"saves": saves, "snapshots": save_snapshots}


@dataclass(frozen=True)
class Stored:
    """A row's key (a save's id; a snapshot's save id and day), its state as read, and the digest its row names."""

    key: tuple[int, ...]
    state: str
    rules_digest: str


def whole_rows(conn: Connection, kind: Kind, after: tuple[int, ...] | None, limit: int) -> list[Stored]:
    """Up to `limit` rows of `kind` whose state carries its own manifest, in key order after `after`."""
    t = _TABLES[kind]
    keys = list(t.primary_key.columns)
    q = select(*keys, t.c.state, t.c.rules_digest).where(carries_own(t.c.state)).order_by(*keys).limit(limit)
    if after is not None:
        q = q.where(tuple_(*keys) > tuple_(*(literal(k) for k in after)))
    return [Stored(tuple(r[:len(keys)]), r.state, r.rules_digest) for r in conn.execute(q)]


def swap(conn: Connection, kind: Kind, row: Stored, state: str) -> bool:
    """Writes `state` over `row`'s only while the row still holds the state read (a compare-and-set); whether it did."""
    t = _TABLES[kind]
    keyed = and_(*(c == k for c, k in zip(t.primary_key.columns, row.key, strict=True)))
    return conn.execute(update(t).where(keyed, t.c.state == row.state).values(state=state)).rowcount == 1


def _unnamed(keep: str) -> ColumnElement[bool]:
    m = save_manifests.c.rules_digest
    return and_(m != keep, not_(exists().where(saves.c.rules_digest == m)),
                not_(exists().where(save_snapshots.c.rules_digest == m)))


def unnamed(conn: Connection, keep: str) -> int:
    """How many manifests no save or snapshot names, `keep`'s aside."""
    return int(conn.execute(select(func.count()).select_from(save_manifests).where(_unnamed(keep))).scalar_one())


def prune(conn: Connection, keep: str) -> int:
    """Deletes the manifests no save or snapshot names, never `keep`'s; how many went."""
    return conn.execute(delete(save_manifests).where(_unnamed(keep))).rowcount
