"""The saved ends week two's chapters play on from (tests/weektwo/ends.py), written from plays from the start, and the
typical route's heavy-step readings (tools/saves_plan.py plans their parts).

    python tools/chapter_saves.py --write    # from app/, with PYTHONPATH=.: write all of them, each chapter's under its key
    python tools/chapter_saves.py --write babysitter rebased-eight readings-eight-0   # only those parts, by name: a route's
                                                       # ends, typical's rebased saves (they read typical's saved ends) or readings
    python tools/chapter_saves.py --write sharp-2      # a link of a route's chain: reads the link before's ends
    python tools/chapter_saves.py --prune    # delete the directories of keys no chapter has today

A chapter's directory is named by its key (tests/weektwo/keys.py), so a change to what the chapter's play depends on is a
new directory and no save outlives it, while a chapter before the change keeps its own.
CI builds each part in a job of its own (it starts from the saves the last nightly cached, and writes only the chapters whose key is new), since no route's plays and no reading
need another; the rebased parts read typical's saved ends, so they run once typical's part has, and a chain too long for
one job is written in links, each after the one before. Which chapters make a link, a rebased group or a readings part is
planned from each chapter's measured cost (tools/saves_plan.py). Locally, run it to make week two's job fast.
"""
import gc
import os
import shutil
import sys
import time
from pathlib import Path

from tests.weektwo import counters, ends, keys, rebased, verdicts
from tools import saves_plan
from tests.daytwo.player import DayTwoPlayer
from tests.weektwo.routes import BEFORE, SAVED, laters, play_on, played

PLAN = saves_plan.today()
LINKS = {link.part: link for link in PLAN.links}
"""A route's chain in links, by part (`typical-1`): each after the one before, which a link plays on from the saved end of."""
LINKED = frozenset(link.route for link in PLAN.links)
ROUTES = frozenset(name for names in SAVED.values() for name in names) - LINKED
"""Every route with a saved end written whole, in one part named for it."""
REBASED = {g.part: g.chapters for g in PLAN.rebased}
"""typical's rebased saves (ends.rebased_path), by part: each chapter's save, replayed from the decisions of typical's
saved end at it, so a part needs typical's ends and not typical's play from the start."""
READINGS = {r.part: r.spans for r in PLAN.readings}
ALL = ROUTES | frozenset(READINGS) | frozenset(REBASED) | frozenset(LINKS)
"""Every part `--write` takes by name."""


def chapters_of(parts: frozenset[str]) -> list[str]:
    """The chapters whose directories `parts` write into, in order."""
    found = {c for c, names in SAVED.items() for n in names if n in parts & ROUTES}
    found |= {c for n in parts & frozenset(LINKS) for c in link_chapters(n)}
    found |= {c for n in parts & frozenset(REBASED) for c in REBASED[n]}
    found |= {c for n in parts & frozenset(READINGS) for c, _, _ in READINGS[n]}
    return [c for c in keys.ORDER if c in found]


def present(path: Path) -> bool:
    """Whether `path` was written under today's key (its directory is named by it) and need not be written again."""
    if path.exists():
        print(f"event=chapter_saves.kept file={path.name}", flush=True)
    return path.exists()


def prune(root: Path) -> list[str]:
    """Delete the directories under `root` that no chapter's key names today; the names removed."""
    wanted = {ends.key(c) for c in keys.ORDER}
    gone = sorted(d.name for d in root.iterdir() if d.is_dir() and d.name not in wanted) if root.is_dir() else []
    for name in gone:
        shutil.rmtree(root / name)
    return gone


def put(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data) if isinstance(data, bytes) else path.write_text(data)


def write(parts: frozenset[str] = ALL) -> int:
    """The saves of `parts`."""
    unknown = parts - ALL
    if unknown:
        print(f"no saved part {sorted(unknown)}: {sorted(ALL)}", file=sys.stderr)
        return 2
    write_ends(parts & ROUTES)
    for name in (n for n in LINKS if n in parts):
        write_link(name)
    for name in sorted(parts & frozenset(REBASED)):
        write_rebased(name)
    for name in sorted(parts & frozenset(READINGS)):
        write_readings(name)
    for chapter in chapters_of(parts):
        put(ends.manifest(chapter), ends.manifest_json(chapter))
    print(f"event=chapter_saves.write chapters={','.join(chapters_of(parts))} root={ends.root()}")
    return 0


def write_ends(routes: frozenset[str]) -> None:
    for chapter, names in SAVED.items():
        for name in (n for n in names if n in routes and not present(ends.player_path(chapter, n))):
            started = time.process_time()
            write_end(chapter, name, played(chapter, name), started)


def write_end(chapter: str, name: str, p: DayTwoPlayer, started: float) -> None:
    data = ends.dump(p)
    put(ends.player_path(chapter, name), data)
    print(f"event=chapter_saves.player chapter={chapter} route={name} bytes={len(data)} "
          f"cpu_s={time.process_time() - started:.1f}", flush=True)


def link_chapters(name: str) -> list[str]:
    """The chapters link `name` writes the route's ends of, in order."""
    return list(LINKS[name].chapters)


def frozen(p: DayTwoPlayer) -> DayTwoPlayer:
    """`p`, a saved end just loaded to be played on, with everything alive parked out of the collector's reach: the play
    then never walks the save's objects (measured at about 8% of a late chapter's play)."""
    gc.collect()
    gc.freeze()
    return p


def write_link(name: str) -> None:
    """Link `name`'s ends: played from the start for the first link, else on from the saved end before its first. An end
    already saved under today's key is loaded, not played, so only the chapters after a change replay."""
    route = LINKS[name].route
    p: DayTwoPlayer | None = None
    for chapter in link_chapters(name):
        started = time.process_time()
        if present(ends.player_path(chapter, route)):
            p = ends.load(chapter, route, laters(chapter, route))
            continue
        if chapter == "week1":
            p = played(chapter, route)
        else:
            if p is None:
                p = frozen(ends.load(BEFORE[chapter], route, laters(BEFORE[chapter], route)))
            p = play_on(p, laters(chapter, route))
        write_end(chapter, route, p, started)


def write_rebased(name: str) -> None:
    for chapter in (c for c in REBASED[name] if not present(ends.rebased_path(c))):
        started = time.process_time()
        saved = ends.load(chapter, "typical", laters(chapter, "typical"))
        text = ends.rebased_json(rebased.written(chapter, saved))
        put(ends.rebased_path(chapter), text)
        print(f"event=chapter_saves.rebased chapter={chapter} bytes={len(text)} "
              f"cpu_s={time.process_time() - started:.1f}", flush=True)


def typical_through(chapter: str) -> DayTwoPlayer:
    """typical's play through `chapter` from its saved end, else (the last chapter's end is saved by no route) on from the
    saved end of the chapter before: the play without replaying the chapters before."""
    if "typical" in SAVED.get(chapter, ()):
        return ends.load(chapter, "typical", laters(chapter, "typical"))
    before = frozen(ends.load(BEFORE[chapter], "typical", laters(BEFORE[chapter], "typical")))
    return play_on(before, laters(chapter, "typical"))


def write_readings(name: str) -> None:
    """The readings part `name`: each span's heavy steps of typical's play through its chapter, read one by one, each
    reading in a file of its own, so a part split differently later leaves no file behind."""
    table = saves_plan.load()
    for chapter, first, after in READINGS[name]:
        wanted = range(first, after if after is not None else saves_plan.heavy_count(table, chapter))
        if all(present(ends.readings_path(chapter, i)) for i in wanted):
            continue
        p, later = typical_through(chapter), verdicts.CHAPTERS[chapter]
        steps = {v.label: v.steps for v in verdicts.chapter_visits(p, later)}
        for i, (label, k) in enumerate(verdicts.heavy_steps(p, later)[first:after], first):
            if ends.readings_path(chapter, i).exists():
                continue
            started = time.process_time()
            decides = counters.decides(steps[label][k], p.rules)
            put(ends.readings_path(chapter, i), ends.readings_json({(label, k): decides}))
            print(f"event=chapter_saves.reading part={name} chapter={chapter} index={i} step={label}:{k} "
                  f"cpu_s={time.process_time() - started:.1f}", flush=True)


HASH_SEED = "0"
"""A pickled set lists its items in hash order, which differs per process unless the seed is fixed: under one seed an
unchanged play is rewritten byte for byte, so a rewrite changes only the ends whose play changed."""


def main(argv: list[str]) -> int:
    if argv[:1] == ["--write"] and os.environ.get("PYTHONHASHSEED") != HASH_SEED:
        os.execve(sys.executable, [sys.executable, *sys.argv], {**os.environ, "PYTHONHASHSEED": HASH_SEED})
    if argv == ["--prune"]:
        print(f"event=chapter_saves.prune removed={','.join(prune(ends.root())) or 'none'}")
        return 0
    if argv[:1] == ["--write"]:
        return write(frozenset(argv[1:]) or ALL)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
