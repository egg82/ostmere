"""`python -m ashfall_app.saves check | replay <save> --from <day> | restore <save> --from <day> [--until <n>]
--keep <file> | strip [--dry-run]` against the database DATABASE_URL names, under this build's rules (check.py,
support.py, strip.py). A day is the UTC day number (days since 1970-01-01) a snapshot was taken on. Prints counts
and ids, never a state."""

import argparse
import os
import sys
from pathlib import Path

from .. import logs
from ..clock import system
from ..db.engine import open_database
from ..opening.lock import load_lock
from ..opening.renames import load_renames
from ..opening.schema import load_opening
from .check import check
from .ruleset import ruleset
from .strip import strip
from .support import replay, restore


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m ashfall_app.saves")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="dry-rebase every live save; exit 1 if any fails")
    r = sub.add_parser("replay", help="rebuild a save from a day's snapshot and its decisions, and compare")
    r.add_argument("save", type=int)
    r.add_argument("--from", dest="day", type=int, required=True)
    w = sub.add_parser("restore", help="set a save back to a day's snapshot plus decisions up to --until")
    w.add_argument("save", type=int)
    w.add_argument("--from", dest="day", type=int, required=True)
    w.add_argument("--until", type=int, default=None)
    w.add_argument("--keep", type=Path, required=True, help="file to write the save's row to first (must not exist)")
    s = sub.add_parser("strip", help="write every save and snapshot without its manifest, then prune unnamed ones")
    s.add_argument("--dry-run", action="store_true", help="count what would be done and write nothing")
    return p


def main(argv: list[str]) -> int:
    args = _parser().parse_args(argv)
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2
    logs.setup()
    rs = ruleset(load_opening(), load_renames(), os.environ.get("BUILD_VERSION", "dev"), load_lock().release)
    database = open_database(url)
    try:
        if args.command == "check":
            done = check(database.engine, rs)
            print(f"total={done.total} ok={done.ok} failed={done.failed} newer={done.newer}")
            return 1 if done.failed else 0
        if args.command == "replay":
            got = replay(database.engine, rs, args.save, args.day)
            print(f"save={args.save} decisions={got.decisions} time={got.save.time} matches={got.matches}")
            return 0 if got.matches else 1
        if args.command == "strip":
            got = strip(database.engine, rs, args.dry_run)
            print(f"dry_run={args.dry_run} stripped={got.stripped} whole={got.whole} changed={got.changed} "
                  f"pruned={got.pruned}")
            return 0
        n = restore(database.engine, rs, system, args.save, args.day, args.until, args.keep)
        print(f"save={args.save} restored decisions={n} kept={args.keep}")
        return 0
    finally:
        database.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
