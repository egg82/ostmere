"""The release lock: check the opening against what has been released, or record a release.

    python tools/content_lock.py --check    # print every problem; exit 1 if any
    python tools/content_lock.py --write    # record this content in ashfall_app/opening/released/ids.json
    python tools/content_lock.py --reset    # before cutover only: the lock from this content alone

Run from app/. --write refuses while any problem is not out_of_date (a removal to map, or a forbidden change). Change
classes: engine DESIGN.txt, "Release lock"; the checks: ashfall_app/opening/lock_checks.py.
"""
import sys

from ashfall_app.opening.lock import LOCK, load_lock, lock_text, merged, snapshot
from ashfall_app.opening.lock_checks import problems
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening, to_rules

LAUNCHED = True
"""Flipped once saves persist for players (the cutover): from then on the lock is never reset, only extended."""


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in ("--check", "--write", "--reset"):
        print(__doc__, file=sys.stderr)
        return 2
    o = load_opening()
    renames = load_renames()
    now = snapshot(o, to_rules(o), renames)
    if argv[0] == "--reset":
        if LAUNCHED:
            print("refused: the game has launched, so the lock is only ever extended (--write)", file=sys.stderr)
            return 1
        LOCK.write_text(lock_text(now))
        print(f"reset {LOCK}")
        return 0
    lock = load_lock()
    found = problems(lock, now, renames)
    for p in found:
        print(f"{p.cls}: {p.message}")
    if argv[0] == "--check":
        return 1 if found else 0
    if any(p.cls != "out_of_date" for p in found):
        print("refused: fix the problems above first", file=sys.stderr)
        return 1
    LOCK.write_text(lock_text(merged(lock, now)))
    print(f"wrote {LOCK}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
