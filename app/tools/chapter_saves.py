"""The saved ends week two's chapters play on from (tests/weektwo/ends.py), written from plays from the start.

    python tools/chapter_saves.py --write    # from app/, with PYTHONPATH=.: write the saves under ends.key()
    python tools/chapter_saves.py --write typical sharp   # only those routes' ends (and the rebased saves with typical)
    python tools/chapter_saves.py --key      # print the key

The directory is named by the key, so a change to what the saves depend on is a new directory and no save outlives it.
CI builds it once per key (tools/saves_cache.py), each route's chain in a job of its own, since no route's plays read
another's; locally, run it to make week two's job fast.
"""
import os
import sys
import time

from tests.daythree.content import rules3
from tests.weektwo import ends, rebased
from tests.weektwo.routes import SAVED, played

ALL = frozenset(name for names in SAVED.values() for name in names)
"""Every route with a saved end."""


def write(routes: frozenset[str] = ALL) -> int:
    """The saved ends of `routes`, and the rebased saves when typical is one of them; all of them clear the directory."""
    unknown = routes - ALL
    if unknown:
        print(f"no saved route {sorted(unknown)}: {sorted(ALL)}", file=sys.stderr)
        return 2
    ends.golden().mkdir(parents=True, exist_ok=True)
    for old in ends.golden().iterdir() if routes == ALL else ():
        old.unlink()
    for chapter, names in SAVED.items():
        for name in (n for n in names if n in routes):
            started = time.process_time()
            data = ends.dump(played(chapter, name))
            ends.player_path(chapter, name).write_bytes(data)
            print(f"event=chapter_saves.player chapter={chapter} route={name} bytes={len(data)} "
                  f"cpu_s={time.process_time() - started:.1f}", flush=True)
    for chapter in rebased.OLD if "typical" in routes else ():
        started = time.process_time()
        text = ends.rebased_json(rebased.written(chapter, played(chapter, "typical")))
        ends.rebased_path(chapter).write_text(text)
        print(f"event=chapter_saves.rebased chapter={chapter} bytes={len(text)} "
              f"cpu_s={time.process_time() - started:.1f}", flush=True)
    ends.manifest().write_text(ends.manifest_json(rules3()))
    print(f"event=chapter_saves.write files={len(list(ends.golden().iterdir()))} dir={ends.golden()}")
    return 0


HASH_SEED = "0"
"""A pickled set lists its items in hash order, which differs per process unless the seed is fixed: under one seed an
unchanged play is rewritten byte for byte, so a rewrite changes only the ends whose play changed."""


def main(argv: list[str]) -> int:
    if argv[:1] == ["--write"] and os.environ.get("PYTHONHASHSEED") != HASH_SEED:
        os.execve(sys.executable, [sys.executable, *sys.argv], {**os.environ, "PYTHONHASHSEED": HASH_SEED})
    if argv == ["--key"]:
        print(ends.key())
        return 0
    if argv[:1] == ["--write"]:
        return write(frozenset(argv[1:]) or ALL)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
