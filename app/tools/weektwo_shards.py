"""The shards of CI's `playthrough-week-two` job: which job runs each week-two test (tests/weektwo).

A test goes to the shard naming its play (tests/weektwo/conftest.py, `play_of`) as "chapter-route", else the one naming
its play's chapter, else, reading no play, the one naming NO_PLAY. A test marked `weektwo_shard(name)` goes to that shard whatever it reads. Every reader of a play lands in one shard, so no job
plays another's plays again. Kept out of tests/weektwo so a change here leaves the saved ends' key alone (ends.py).

WEEKTWO_SHARD=<name> runs one shard; unset, every test runs.
WEEKTWO_SLICE=<chapter>[,<chapter>...] runs a pull request's slice: the tests that play those chapters, each from the saved
end of the chapter before (ASHFALL_BASE_KEYS, tests/weektwo/ends.py), less the ones that read a chapter's own saved end, readings
or rebased save, which only the full run writes. WEEKTWO_SLICE=smoke runs the tests marked `smoke`, played from the start.
WEEKTWO_FILES=<repo-relative path>[,...] adds every test of those week-two test files to a slice.
Run from app/: python -m tools.weektwo_shards --check   exits 1 unless each week-two playthrough test is selected by
                                                        exactly one shard, so a chapter added to routes.CHAPTERS fails
                                                        CI until a shard names it; then prints `matrix=<json>`, the
                                                        shard names, which CI's `shards-cover` hands the week-two job.
"""
import json
import os
import sys
from pathlib import Path

import pytest

from tools.shards import collected

NO_PLAY = "no-play"
SHARDS: dict[str, frozenset[str]] = {
    "eight": frozenset({"eight", NO_PLAY}),
    "nine": frozenset({"nine"}),
    "eleven": frozenset({"eleven"}),
    "twelve-typical": frozenset({"twelve-typical"}),
    "twelve": frozenset({"twelve"}),
    "fifteen": frozenset({"fifteen"}),
    "sixteen": frozenset({"sixteen"}),
    "eighteen": frozenset({"eighteen"}),
    "nineteen": frozenset({"nineteen"}),
    "twentytwo": frozenset({"twentytwo"}),
    "twentythree": frozenset({"twentythree"}),
    "twentyfive-sharp": frozenset({"twentyfive-sharp"}),
    "twentyfive": frozenset({"twentyfive"}),
    "makers": frozenset({"makers"}),
}
NIGHTLY_ONLY = frozenset({"eight", "eighteen", "nineteen", "twentytwo", "twentythree", "twentyfive-sharp", "twentyfive"})
"""The shards a pull request's slice does not play: each took over 300 s in the last nightly (a slice job's `timeout-minutes`,
which setup takes about 35 s of), or in a slice, for day twenty-five (typical about 390 s, whenever about 280 s, sharp about
590 s to build). The nightly plays them. A shard moves out of this set when it is split or sped up to fit, never by raising
a timeout; a shard not named plays in its chapter's slice."""
ENV = "WEEKTWO_SHARD"
SLICE = "WEEKTWO_SLICE"
FILES = "WEEKTWO_FILES"
SMOKE = "smoke"
WEEK_TWO = Path(__file__).resolve().parents[1] / "tests" / "weektwo"
REPO = WEEK_TWO.parents[2]
ARGS = ["tests/weektwo"]
SELECT = ("-m", "playthrough")


def shard_of(play: tuple[str, str] | None, named: str | None = None) -> str | None:
    """The shard a test reading `play` runs in, or None when no shard names it. `named` is the test's own
    `weektwo_shard` marker, which overrides its play."""
    if named is not None:
        return named if named in SHARDS else None
    keys = ("-".join(play), play[0]) if play is not None else (NO_PLAY,)
    for key in keys:
        found = [name for name, held in SHARDS.items() if key in held]
        if found:
            return found[0]
    return None


def shards_of_chapter(chapter: str) -> list[str]:
    """The shards that play `chapter`: those holding the chapter itself or one of its routes."""
    return [name for name, held in SHARDS.items() if any(k == chapter or k.startswith(chapter + "-") for k in held)]


def slice_shards(chapters: list[str], all_shards: bool) -> tuple[list[str], list[str]]:
    """(the shards a slice plays, the ones it leaves to the nightly): those of each touched chapter, or every shard when a
    week-two test file changed, since which shard a file's tests are in is known only by collecting."""
    wanted = list(SHARDS) if all_shards else [n for c in chapters for n in shards_of_chapter(c)]
    return [n for n in wanted if n not in NIGHTLY_ONLY], [n for n in wanted if n in NIGHTLY_ONLY]


def chosen() -> str | None:
    """The shard this session runs (ENV), None for all of them."""
    name = os.environ.get(ENV) or None
    if name is not None and name not in SHARDS:
        raise pytest.UsageError(f"{ENV}={name!r} is not a week-two shard: {sorted(SHARDS)}")
    return name


def sliced() -> frozenset[str] | None:
    """The chapters of this session's slice (SLICE), {SMOKE} for the smoke, None for no slice."""
    names = [n for n in os.environ.get(SLICE, "").split(",") if n]
    return frozenset(names) if names else None


def files() -> frozenset[Path]:
    return frozenset((REPO / f).resolve() for f in os.environ.get(FILES, "").split(",") if f)


def in_week_two(item: pytest.Item) -> bool:
    return WEEK_TWO in item.path.parents


def check() -> int:
    env = {k: v for k, v in os.environ.items() if k != ENV}
    whole = collected(ARGS, SELECT, env)
    picked = {name: collected(ARGS, SELECT, {**env, ENV: name}) for name in SHARDS}
    print(f"week two: {len(whole)} tests; " + ", ".join(f"{name} {len(ids)}" for name, ids in picked.items()))
    seen: dict[str, list[str]] = {}
    for name, ids in picked.items():
        for node in ids:
            seen.setdefault(node, []).append(name)
    missing = sorted(whole - set(seen))
    twice = sorted(node for node, names in seen.items() if len(names) > 1)
    extra = sorted(set(seen) - whole)
    for label, nodes in (("in no shard", missing), ("in more than one shard", twice), ("only in a shard", extra)):
        for node in nodes[:10]:
            print(f"{label}: {node} {seen.get(node, [])}")
    unknown = sorted(NIGHTLY_ONLY - set(SHARDS))
    for name in unknown:
        print(f"NIGHTLY_ONLY names no shard: {name}")
    return 1 if missing or twice or extra or unknown else 0


if __name__ == "__main__":
    if sys.argv[1:] != ["--check"]:
        sys.exit(__doc__)
    failed = check()
    if failed:
        sys.exit(failed)
    print("matrix=" + json.dumps(list(SHARDS)))
