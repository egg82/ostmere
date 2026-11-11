"""Replay every kept snapshot of every save in a dump through its logged decisions under this build's engine and
rules, and say whether, and by when, each stops matching what was stored (engine DESIGN.txt, "Shipping the evaluation
change"). Read-only: it reads one JSON file and prints logfmt; no database.

    python -m tools.replay_check <dump.json>      # from app/; exit 1 when any snapshot mismatches

The dump is one JSON object of row lists, keyed by column name (psql's json_agg of each table):
  saves      id, state, format, rules_digest, decisions, game_time, ended_at, build, release
  snapshots  save_id, day, state, rules_digest, decisions
  decisions  save_id, n, at, verb, rules_digest
  manifests  rules_digest, manifest (save_manifests: a stripped state is read with its digest's)
Each snapshot replays as saves/support.py's `replay` does, and is compared at every later snapshot of its save (each
holds the save just after its decision) and at the stored row. A line per snapshot:
  save=<id> snapshot=<day> match=true|false|unknown first_diff_at=<t>|- last_match_at=<t>|- crosses_release=<bool>
first_diff_at is the game time of the first checkpoint that differs (or of a logged decision the replay refuses), so
the divergence lies after last_match_at and by first_diff_at. crosses_release says the span holds a rules digest other
than this build's: such a span also differs for the rebase's instant, not only for engine code. `unknown` is a span
that cannot be replayed (a gap in the log, a save or verb this build cannot read), with its reason. Then a line per save that
mismatches, with the day its mismatching snapshots are all gone (the writer drops a snapshot older than SNAPSHOT_DAYS
at its next write, saves/write.py), and a summary.
"""
import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ashfall_app import engine as e
from ashfall_app.db.manifests import whole
from ashfall_app.db.saves import DecisionRecord, SaveRecord, SnapshotRecord
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.interface import Ruleset, Unavailable
from ashfall_app.saves.load import load
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.support import SupportError, check_gapless, snapshot_save
from ashfall_app.saves.write import SNAPSHOT_DAYS

type Row = dict[str, Any]
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


@dataclass(frozen=True)
class Checked:
    save_id: int
    day: int
    match: bool | None
    """None: the span could not be replayed (`reason` says why)."""
    first_diff_at: int | None
    last_match_at: int | None
    crosses_release: bool
    reason: str = ""


def save_record(r: Row, held: dict[str, str]) -> SaveRecord:
    """A dumped saves row as the row type load() reads, its state whole with `held`'s manifest for its digest; the
    columns it does not read are left neutral."""
    return SaveRecord(id=r["id"], account_id=0, started_at=_EPOCH, updated_at=_EPOCH,
                      state=whole(r["state"], held.get(r["rules_digest"])),
                      format=r["format"], rules_digest=r["rules_digest"], decisions=r["decisions"],
                      game_time=r["game_time"], ended_at=r.get("ended_at"), build=r.get("build"),
                      release=r.get("release"), number=None, camp_level=None, deleted_at=None)


def check_snapshot(rs: Ruleset, row: SaveRecord, snap: SnapshotRecord, snaps: list[SnapshotRecord],
                   log: list[DecisionRecord]) -> Checked:
    """Replay `snap` through the decisions after it, comparing at each later snapshot in `snaps` and at the row."""
    later = [d for d in log if d.n > snap.decisions]
    digests = {snap.rules_digest, row.rules_digest, *(d.rules_digest for d in later)}
    found = Checked(row.id, snap.day, None, None, None, digests != {rs.digest})
    try:
        check_gapless(row, snap, later)
        save = snapshot_save(rs, row, snap)
        stored = load(row, rs).save
    except SupportError:
        return _with(found, None, None, None, "log_gap")
    except Unavailable:
        return _with(found, None, None, None, "unreadable")
    marks = {s.decisions: s for s in snaps if s.decisions > snap.decisions}
    last = save.time
    for d in later:
        try:
            verb = e.verb_from_json(d.verb)
        except e.StateFormatError:
            return _with(found, None, None, last, "bad_verb")
        try:
            save = e.decide(save, rs.rules, d.at, verb)
        except (e.InvalidVerbError, e.TimeOrderError):
            return _with(found, False, d.at, last, "refused")
        mark = marks.get(d.n)
        if mark is not None:
            kept = snapshot_save(rs, row, mark)
            if save != kept:
                return _with(found, False, kept.time, last, "snapshot")
            last = kept.time
    if save.time > stored.time or e.advance(save, rs.rules, stored.time) != stored:
        return _with(found, False, stored.time, last, "row")
    return _with(found, True, None, stored.time, "")


def _with(c: Checked, match: bool | None, first: int | None, last: int | None, reason: str) -> Checked:
    return Checked(c.save_id, c.day, match, first, last, c.crosses_release, reason)


def line(c: Checked) -> str:
    match = "unknown" if c.match is None else str(c.match).lower()
    out = (f"save={c.save_id} snapshot={c.day} match={match} first_diff_at={_t(c.first_diff_at)} "
           f"last_match_at={_t(c.last_match_at)} crosses_release={str(c.crosses_release).lower()}")
    return out + (f" reason={c.reason}" if c.reason else "")


def _t(t: int | None) -> str:
    return "-" if t is None else str(t)


def ages_out_day(days: list[int]) -> int:
    """The first UTC day a write drops every one of these snapshots: write.py keeps day d while d >= today -
    SNAPSHOT_DAYS."""
    return max(days) + SNAPSHOT_DAYS + 1


def date_of(day: int) -> str:
    return (_EPOCH + timedelta(days=day)).date().isoformat()


def check_dump(rs: Ruleset, dump: Row) -> list[tuple[SaveRecord, list[Checked]]]:
    apart: list[Row] = dump.get("manifests") or []
    held = {str(m["rules_digest"]): str(m["manifest"]) for m in apart}
    snaps: dict[int, list[SnapshotRecord]] = {}
    for s in dump["snapshots"]:
        snaps.setdefault(s["save_id"], []).append(SnapshotRecord(day=s["day"],
                                                                 state=whole(s["state"], held.get(s["rules_digest"])),
                                                                 rules_digest=s["rules_digest"],
                                                                 decisions=s["decisions"]))
    logs: dict[int, list[DecisionRecord]] = {}
    for d in dump["decisions"]:
        logs.setdefault(d["save_id"], []).append(DecisionRecord(n=d["n"], at=d["at"], kind=d.get("kind", ""),
                                                                verb=d["verb"], rules_digest=d["rules_digest"]))
    found: list[tuple[SaveRecord, list[Checked]]] = []
    for r in sorted(dump["saves"], key=lambda r: r["id"]):
        row = save_record(r, held)
        kept = sorted(snaps.get(row.id, []), key=lambda s: s.day)
        log = sorted(logs.get(row.id, []), key=lambda d: d.n)
        found.append((row, [check_snapshot(rs, row, s, kept, log) for s in kept]))
    return found


def report(found: list[tuple[SaveRecord, list[Checked]]]) -> list[str]:
    """Each snapshot's line, then a line per mismatching save, then the summary."""
    out = [line(c) for _, checks in found for c in checks]
    bad = [(row, [c.day for c in checks if c.match is False]) for row, checks in found]
    bad = [(row, days) for row, days in bad if days]
    for row, days in bad:
        out.append(f"save={row.id} mismatched_snapshots={len(days)} ended={str(row.ended_at is not None).lower()} "
                   f"ages_out_day={ages_out_day(days)} ages_out={date_of(ages_out_day(days))}")
    checks = [c for _, cs in found for c in cs]
    latest = max((ages_out_day(days) for _, days in bad), default=None)
    out.append(f"summary saves={len(found)} snapshots={len(checks)} "
               f"mismatched_saves={len(bad)} mismatched_snapshots={sum(c.match is False for c in checks)} "
               f"unknown_snapshots={sum(c.match is None for c in checks)} "
               f"crossing_release_mismatches={sum(c.match is False and c.crosses_release for c in checks)} "
               f"ended_mismatched={sum(row.ended_at is not None for row, _ in bad)} "
               f"all_aged_out_by={'-' if latest is None else date_of(latest)} (for saves written again by then)")
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.replay_check")
    p.add_argument("dump", type=Path)
    args = p.parse_args(argv)
    rs = ruleset(load_opening(), load_renames(), "replay_check", load_lock().release)
    found = check_dump(rs, json.loads(args.dump.read_text()))
    for text in report(found):
        print(text, flush=True)
    return 1 if any(c.match is False for _, cs in found for c in cs) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
