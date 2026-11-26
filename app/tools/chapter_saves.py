"""The saved ends week two's chapters play on from (tests/weektwo/ends.py), written from plays from the start, and the
typical route's heavy-step readings (ends.READINGS).

    python tools/chapter_saves.py --write    # from app/, with PYTHONPATH=.: write all of them under ends.key()
    python tools/chapter_saves.py --write typical rebased-early readings-early   # only those parts, by name: a route's
                                                       # ends, typical's rebased saves (they read typical's saved ends) or readings
    python tools/chapter_saves.py --write sharp-b      # a link of a route's chain (LINKS): reads the link before's ends
    python tools/chapter_saves.py --key      # print the key

The directory is named by the key, so a change to what the saves depend on is a new directory and no save outlives it.
CI builds it once per key (tools/saves_cache.py), each part in a job of its own, since no route's plays and no reading
need another; the rebased parts read typical's saved ends, so they run once typical's part has, and a chain too long for
one job is written in links, each after the one before. Locally, run it to make week two's job fast.
"""
import os
import sys
import time

from tests.daythree.content import rules3
from tests.weektwo import counters, ends, rebased, verdicts
from tests.daytwo.player import DayTwoPlayer
from tests.weektwo.routes import BEFORE, SAVED, laters, play_on, played

LINKS: dict[str, tuple[str, str, str | None]] = {"typical-a": ("typical", "week1", "eighteen"),
                                                 "typical-b": ("typical", "eighteen", "twentytwo"),
                                                 "typical-c": ("typical", "twentytwo", None),
                                                 "sharp-a": ("sharp", "week1", "eighteen"),
                                                 "sharp-b": ("sharp", "eighteen", "twentytwo"),
                                                 "sharp-c": ("sharp", "twentytwo", None),
                                                 "whenever-a": ("whenever", "week1", "eighteen"),
                                                 "whenever-b": ("whenever", "eighteen", "twentytwo"),
                                                 "whenever-c": ("whenever", "twentytwo", None)}
"""A route's chain in links, by part: (route, the link's first chapter, the next link's first or None for all the rest),
in SAVED's order. CI writes each in a job after the one before, since the whole chain runs past one job's cap; a link
after the first plays on from the saved end before its first chapter, which the link before wrote."""
LINKED = frozenset(route for route, _, _ in LINKS.values())
ROUTES = frozenset(name for names in SAVED.values() for name in names) - LINKED
"""Every route with a saved end written whole, in one part named for it."""
REBASED: dict[str, tuple[str, ...]] = {"rebased-early": ("eight", "nine", "eleven", "twelve"),
                                       "rebased-late": ("fifteen", "sixteen", "eighteen", "nineteen"),
                                       "rebased-later": ("twentytwo", "twentythree")}
"""typical's rebased saves (ends.rebased_path), by part: each chapter's save, replayed from the decisions of typical's
saved end at it, so a part needs typical's ends and not typical's play from the start."""
ALL = ROUTES | frozenset(ends.READINGS) | frozenset(REBASED) | frozenset(LINKS)
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
    for name in (n for n in LINKS if n in parts):
        write_link(name)
    for name in sorted(parts & frozenset(REBASED)):
        write_rebased(name)
    for name in sorted(parts & frozenset(ends.READINGS)):
        write_readings(name)
    ends.manifest().write_text(ends.manifest_json(rules3()))
    print(f"event=chapter_saves.write files={len(list(ends.golden().iterdir()))} dir={ends.golden()}")
    return 0


def write_ends(routes: frozenset[str]) -> None:
    for chapter, names in SAVED.items():
        for name in (n for n in names if n in routes):
            started = time.process_time()
            write_end(chapter, name, played(chapter, name), started)


def write_end(chapter: str, name: str, p: DayTwoPlayer, started: float) -> None:
    data = ends.dump(p)
    ends.player_path(chapter, name).write_bytes(data)
    print(f"event=chapter_saves.player chapter={chapter} route={name} bytes={len(data)} "
          f"cpu_s={time.process_time() - started:.1f}", flush=True)


def link_chapters(name: str) -> list[str]:
    """The chapters link `name` writes the route's ends of, in order."""
    route, first, after = LINKS[name]
    chapters = [c for c, names in SAVED.items() if route in names]
    return chapters[chapters.index(first):chapters.index(after) if after else None]


def write_link(name: str) -> None:
    """Link `name`'s ends: played from the start for the first link, else on from the saved end before its first."""
    route = LINKS[name][0]
    p: DayTwoPlayer | None = None
    for chapter in link_chapters(name):
        started = time.process_time()
        if chapter == "week1":
            p = played(chapter, route)
        else:
            if p is None:
                p = ends.load(BEFORE[chapter], route, laters(BEFORE[chapter], route))
            p = play_on(p, laters(chapter, route))
        write_end(chapter, route, p, started)


def write_rebased(name: str) -> None:
    for chapter in REBASED[name]:
        started = time.process_time()
        saved = ends.load(chapter, "typical", laters(chapter, "typical"))
        text = ends.rebased_json(rebased.written(chapter, saved))
        ends.rebased_path(chapter).write_text(text)
        print(f"event=chapter_saves.rebased chapter={chapter} bytes={len(text)} "
              f"cpu_s={time.process_time() - started:.1f}", flush=True)


def typical_through(chapter: str) -> DayTwoPlayer:
    """typical's play through `chapter` from its saved end, else (the last chapter's end is saved by no route) on from the
    saved end of the chapter before: the play without replaying the chapters before."""
    if "typical" in SAVED.get(chapter, ()):
        return ends.load(chapter, "typical", laters(chapter, "typical"))
    before = ends.load(BEFORE[chapter], "typical", laters(BEFORE[chapter], "typical"))
    return play_on(before, laters(chapter, "typical"))


def write_readings(name: str) -> None:
    """The readings part `name`: each span's heavy steps of typical's play through its chapter, read one by one."""
    for chapter, first, after in ends.READINGS[name]:
        p, later = typical_through(chapter), verdicts.CHAPTERS[chapter]
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
