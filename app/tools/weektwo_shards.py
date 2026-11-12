"""The shards of CI's `playthrough-week-two` job: which job runs each week-two test (tests/weektwo).

A test goes to the shard naming its play (tests/weektwo/conftest.py, `play_of`) as "chapter-route", else the one naming
its play's chapter, else, reading no play, the one naming NO_PLAY. Every reader of a play lands in one shard, so no job
plays another's plays again. Kept out of tests/weektwo so a change here leaves the saved ends' key alone (ends.py).

WEEKTWO_SHARD=<name> runs one shard; unset, every test runs.
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
}
ENV = "WEEKTWO_SHARD"
WEEK_TWO = Path(__file__).resolve().parents[1] / "tests" / "weektwo"
ARGS = ["tests/weektwo"]
SELECT = ("-m", "playthrough")


def shard_of(play: tuple[str, str] | None) -> str | None:
    """The shard a test reading `play` runs in, or None when no shard names it."""
    keys = ("-".join(play), play[0]) if play is not None else (NO_PLAY,)
    for key in keys:
        found = [name for name, held in SHARDS.items() if key in held]
        if found:
            return found[0]
    return None


def chosen() -> str | None:
    """The shard this session runs (ENV), None for all of them."""
    name = os.environ.get(ENV) or None
    if name is not None and name not in SHARDS:
        raise pytest.UsageError(f"{ENV}={name!r} is not a week-two shard: {sorted(SHARDS)}")
    return name


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
    return 1 if missing or twice or extra else 0


if __name__ == "__main__":
    if sys.argv[1:] != ["--check"]:
        sys.exit(__doc__)
    failed = check()
    if failed:
        sys.exit(failed)
    print("matrix=" + json.dumps(list(SHARDS)))
