"""The saved ends week two's chapters play on from (tests/weektwo/ends.py), written from plays from the start, and the
typical route's heavy-step readings (ends.READINGS).

    python tools/chapter_saves.py --write    # from app/, with PYTHONPATH=.: write all of them under ends.key()
    python tools/chapter_saves.py --write typical readings-early   # only those parts: routes' ends (typical's with the
                                                                   # rebased saves) and readings parts by name
    python tools/chapter_saves.py --key      # print the key

The directory is named by the key, so a change to what the saves depend on is a new directory and no save outlives it.
CI builds it once per key (tools/saves_cache.py), each part in a job of its own, since no route's plays and no reading
need another; locally, run it to make week two's job fast.
"""
import os
import sys
import time

from tests.daythree.content import rules3
from tests.weektwo import counters, ends, rebased, verdicts
from tests.weektwo.routes import SAVED, played

ROUTES = frozenset(name for names in SAVED.values() for name in names)
"""Every route with a saved end."""
ALL = ROUTES | frozenset(ends.READINGS)
"""Every part `--write` takes by name."""


def write(parts: frozenset[str] = ALL) -> int:
    """The saves of `parts`; all of them clear the directory first."""
    unknown = parts - ALL
    if unknown:
        print(f"no saved part {sorted(unknown)}: {sorted(ALL)}", file=sys.stderr)
        return 2
    ends.golden().mkdir(parents=True, exist_ok=True)
    for old in ends.golden().iterdir() if parts == ALL else ():
        old.unlink()
    write_ends(parts & ROUTES)
    if "typical" in parts:
        write_rebased()
    for name in sorted(parts & frozenset(ends.READINGS)):
        write_readings(name)
    ends.manifest().write_text(ends.manifest_json(rules3()))
    print(f"event=chapter_saves.write files={len(list(ends.golden().iterdir()))} dir={ends.golden()}")
    return 0


def write_ends(routes: frozenset[str]) -> None:
    for chapter, names in SAVED.items():
        for name in (n for n in names if n in routes):
            started = time.process_time()
            data = ends.dump(played(chapter, name))
            ends.player_path(chapter, name).write_bytes(data)
            print(f"event=chapter_saves.player chapter={chapter} route={name} bytes={len(data)} "
                  f"cpu_s={time.process_time() - started:.1f}", flush=True)


def write_rebased() -> None:
    for chapter in rebased.OLD:
        started = time.process_time()
        text = ends.rebased_json(rebased.written(chapter, played(chapter, "typical")))
        ends.rebased_path(chapter).write_text(text)
        print(f"event=chapter_saves.rebased chapter={chapter} bytes={len(text)} "
              f"cpu_s={time.process_time() - started:.1f}", flush=True)


def write_readings(name: str) -> None:
    """The readings part `name`: each span's heavy steps of typical's play through its chapter, read one by one."""
    for chapter, first, after in ends.READINGS[name]:
        p, later = played(chapter, "typical"), verdicts.CHAPTERS[chapter]
        steps = {v.label: v.steps for v in verdicts.chapter_visits(p, later)}
        found: dict[tuple[str, int], bool] = {}
        for label, i in verdicts.heavy_steps(p, later)[first:after]:
            started = time.process_time()
            found[label, i] = counters.decides(steps[label][i], p.rules)
            print(f"event=chapter_saves.reading part={name} chapter={chapter} step={label}:{i} "
                  f"cpu_s={time.process_time() - started:.1f}", flush=True)
        ends.readings_path(chapter, first).write_text(ends.readings_json(found))


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
