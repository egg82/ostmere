"""Support tools over one save's day snapshots and decision log (`python -m ashfall_app.saves replay|restore`).

replay: the save rebuilt from a day's snapshot by replaying the logged decisions after it, compared with the save as
stored (both at the stored game time). restore: the save set back to a day's snapshot, plus its logged decisions up
to a count, after the row as it stands is written to a file of the operator's (nothing is lost). The decisions and
snapshots numbered above the count go with it, so the next decision is numbered on from it. Lines stay as they are.
A decision log with a gap (pruned past its 30 days), or a count the snapshot is already past, is refused."""

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from sqlalchemy import Engine

from .. import engine as e
from ..clock import Clock
from ..db import saves as rows
from . import write
from .interface import NotFound, Ruleset
from .load import load
from .manifest import registered


class SupportError(Exception):
    pass


@dataclass(frozen=True)
class Replayed:
    save: e.Save
    decisions: int
    matches: bool
    """The replay advanced to the stored save's time equals the stored save."""


def _rebuilt(engine: Engine, rs: Ruleset, save_id: int, day: int, until: int | None) -> tuple[rows.SaveRecord, e.Save, int]:
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
        snap = rows.snapshot(conn, save_id, day)
        later = rows.decisions_after(conn, save_id, snap.decisions) if snap else []
    if row is None:
        raise NotFound(f"save {save_id}")
    if snap is None:
        raise SupportError(f"save {save_id} has no snapshot for day {day}")
    if until is not None and until < snap.decisions:
        raise SupportError(f"save {save_id}'s snapshot of day {day} already holds {snap.decisions} decisions, past {until}")
    later = [d for d in later if until is None or d.n <= until]
    check_gapless(row, snap, later)
    save = snapshot_save(rs, row, snap)
    for d in later:
        save = e.decide(save, rs.rules, d.at, e.verb_from_json(d.verb))
    return row, save, snap.decisions + len(later)


def check_gapless(row: rows.SaveRecord, snap: rows.SnapshotRecord, later: list[rows.DecisionRecord]) -> None:
    """Raise SupportError unless `later` are the decisions numbered on from the snapshot's, with none missing."""
    if [d.n for d in later] != list(range(snap.decisions + 1, snap.decisions + 1 + len(later))):
        raise SupportError(f"save {row.id}'s decision log has a gap after {snap.decisions}")


def snapshot_save(rs: Ruleset, row: rows.SaveRecord, snap: rows.SnapshotRecord) -> e.Save:
    """The save a day's snapshot of `row` holds, read under `rs` as a stored save is (load.py), whatever release
    wrote it."""
    as_row = replace(row, state=snap.state, rules_digest=snap.rules_digest, format=json.loads(snap.state)["format"],
                     release=0)
    return load(as_row, rs).save


def replay(engine: Engine, rs: Ruleset, save_id: int, day: int) -> Replayed:
    row, save, n = _rebuilt(engine, rs, save_id, day, None)
    stored = load(row, rs).save
    matches = save.time <= stored.time and e.advance(save, rs.rules, stored.time) == stored
    return Replayed(save=save, decisions=n, matches=matches)


def restore(engine: Engine, rs: Ruleset, clock: Clock, save_id: int, day: int, until: int | None,
            keep: Path) -> int:
    """The decisions count the save is restored to. The row as it stood is written to `keep` first, which must not
    exist."""
    _, save, n = _rebuilt(engine, rs, save_id, day, until)
    rs = registered(engine, rs)
    with engine.begin() as conn:
        row = rows.save(conn, save_id, None, lock=True)
        if row is None:
            raise NotFound(f"save {save_id}")
        with keep.open("x") as f:
            json.dump(asdict(row), f, default=str)
        rows.write(conn, save_id, clock(), write.written(save, n, rs))
        rows.delete_decisions_above(conn, save_id, n)
        rows.delete_snapshots_above(conn, save_id, n)
    return n
