"""A step's write as one statement, so the save's row lock is held over one round trip for it rather than five to eight:
the save's row, the lines the step added, for a decision its log entry (older entries pruned) and the day's snapshot
(older days pruned), and the recent decisions the step's repeats are counted from. The parts are data-modifying CTEs of
one SELECT, built once per shape with bound parameters (SQLAlchemy keys and compiles a construct once and reuses it);
they share one snapshot, so what is read of the log is the log as it stands before the statement, plus the
entry it adds, less what it prunes. What is written when, and what is pruned, is saves/ (write.py); this module only
writes."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from typing import Any

from sqlalchemy import (
    ARRAY, BigInteger, CTE, ColumnElement, Connection, Integer, Select, Text, and_, bindparam, delete, exists,
    func, insert, literal_column, or_, select, union_all,
)
from sqlalchemy.dialects.postgresql import aggregate_order_by, insert as pg_insert

from .saves import LISTED, WRITING, DecisionRecord, Listed, Written, as_listed, writing
from .tables import save_decisions, save_lines, save_snapshots, saves


@dataclass(frozen=True)
class Log:
    """What a decision adds to the save's history: its log entry, and the day's snapshot, each with what is pruned."""

    entry: DecisionRecord
    wall_from: datetime
    """Log entries made before this wall time go."""
    day: int
    """The UTC day whose snapshot the step takes, unless the save has one."""
    day_from: int
    """When the snapshot was taken, snapshots of earlier days than this go."""


def write_step(conn: Connection, save_id: int, now: datetime, w: Written, lines: Sequence[tuple[int, str]],
               log: Log | None, since: Mapping[str, int] | None) -> tuple[Listed, list[DecisionRecord]]:
    """The save as written, and its logged decisions of each kind in `since` made at or after its game time (none
    without `since`), the step's own entry among them."""
    params = writing(save_id, now, w) | {"line_at": [at for at, _ in lines], "line_key": [key for _, key in lines],
                                         "save_id": save_id}
    if log is not None:
        d = log.entry
        params |= {"now": now, "l_n": d.n, "l_at": d.at, "l_kind": d.kind, "l_verb": d.verb, "l_digest": d.rules_digest,
                   "l_context": d.context, "wall_from": log.wall_from, "day": log.day, "day_from": log.day_from}
    if since is not None:
        for i, (kind, at) in enumerate(since.items()):
            params |= {f"s_kind{i}": kind, f"s_at{i}": at}
    row = conn.execute(_statement(log is not None, None if since is None else len(since)), params).one()
    return as_listed(row), [DecisionRecord(**d) for d in row.recent or ()]


@cache
def _statement(logged: bool, kinds: int | None) -> Select[Any]:
    """`write_step`'s statement for a step that logs a decision or not and reads `kinds` kinds of recent decisions."""
    upd = WRITING.returning(*LISTED, saves.c.state).cte("upd")
    parts = [_lines()]
    entry: CTE | None = None
    if logged:
        entry, more = _logged(upd)
        parts += [entry, *more]
    recent: ColumnElement[Any] = literal_column("NULL") if kinds is None else _recent(kinds, entry, logged)
    return select(*(upd.c[c.name] for c in LISTED), recent.label("recent")).select_from(upd).add_cte(*parts)


def _lines() -> CTE:
    """The lines (the arrays `line_at` and `line_key`, possibly empty), numbered on from the save's last."""
    given = func.unnest(bindparam("line_at", type_=ARRAY(BigInteger)), bindparam("line_key", type_=ARRAY(Text))
                        ).table_valued("at", "key", with_ordinality="i").render_derived()
    last = select(func.coalesce(func.max(save_lines.c.n), -1)).where(
        save_lines.c.save_id == bindparam("save_id", type_=BigInteger)).scalar_subquery()
    return insert(save_lines).from_select(
        ["save_id", "n", "at", "key"],
        select(bindparam("save_id", type_=BigInteger), last + given.c.i, given.c.at, given.c.key),
    ).returning(save_lines.c.n).cte("lines")


def _logged(upd: CTE) -> tuple[CTE, list[CTE]]:
    """The entry's insert (its CTE, which the recent read joins) and the pruning and snapshot statements."""
    c = save_decisions.c
    save = bindparam("save_id", type_=BigInteger)
    entry = insert(save_decisions).values(
        save_id=save, n=bindparam("l_n", type_=c.n.type), at=bindparam("l_at", type_=c.at.type),
        wall=bindparam("now", type_=c.wall.type), kind=bindparam("l_kind", type_=c.kind.type),
        verb=bindparam("l_verb", type_=c.verb.type), rules_digest=bindparam("l_digest", type_=c.rules_digest.type),
        context=bindparam("l_context", type_=c.context.type),
    ).returning(c.n, c.at, c.kind, c.verb, c.rules_digest, c.context).cte("entry")
    wall_from = bindparam("wall_from", type_=c.wall.type)
    pruned = delete(save_decisions).where(c.save_id == save, c.wall < wall_from).returning(c.n).cte("pruned")
    day = bindparam("day", type_=Integer)
    taken = exists().where(save_snapshots.c.save_id == save, save_snapshots.c.day == day)
    snapped = pg_insert(save_snapshots).from_select(
        ["save_id", "day", "state", "rules_digest", "decisions"],
        select(upd.c.id, day, upd.c.state, bindparam("l_digest", type_=Text), bindparam("l_n", type_=Integer))
        .where(~taken)).on_conflict_do_nothing(index_elements=["save_id", "day"]).returning(save_snapshots.c.day
                                                                                          ).cte("snapped")
    s = save_snapshots.c
    unsnapped = delete(save_snapshots).where(s.save_id == save, s.day < bindparam("day_from", type_=Integer),
                                             exists().where(snapped.c.day.is_not(None))
                                             ).returning(s.day).cte("unsnapped")
    return entry, [pruned, snapped, unsnapped]


def _recent(kinds: int, entry: CTE | None, logged: bool) -> ColumnElement[Any]:
    """The matching logged decisions, in order, as a JSON array: those stored and not pruned, then the entry."""
    c = save_decisions.c

    def matching(t: Any) -> ColumnElement[bool]:
        return or_(*(and_(t.kind == bindparam(f"s_kind{i}", type_=Text), t.at >= bindparam(f"s_at{i}", type_=BigInteger))
                     for i in range(kinds)))
    stored = select(c.n, c.at, c.kind, c.verb, c.rules_digest, c.context).where(
        c.save_id == bindparam("save_id", type_=BigInteger), matching(c))
    if logged:
        stored = stored.where(c.wall >= bindparam("wall_from", type_=c.wall.type))
    found = stored if entry is None else union_all(
        stored, select(entry.c.n, entry.c.at, entry.c.kind, entry.c.verb, entry.c.rules_digest, entry.c.context)
        .where(matching(entry.c)))
    u = found.subquery("found")
    one = func.json_build_object("n", u.c.n, "at", u.c.at, "kind", u.c.kind, "verb", u.c.verb,
                                 "rules_digest", u.c.rules_digest, "context", u.c.context)
    every = func.coalesce(func.json_agg(aggregate_order_by(one, u.c.n)), literal_column("'[]'::json"))
    return select(every).select_from(u).scalar_subquery()
