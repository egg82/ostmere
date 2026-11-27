"""The three shards of CI's `tests` job (docs/engineering.md, "Fast from the start").

Run from app/: python -m tools.shards a|b|c [pytest args]  runs one shard (what CI does);
               python -m tools.shards --check             exits 1 unless the shards together collect what one
                                                          unsharded run does (CI's `shards-cover` job).
Shard A is the three heaviest directories and shard C is tests/rules; shard B is everything else, as an --ignore of
those same paths, so a new test directory lands in B and nothing falls between the shards.
"""
import os
import subprocess
import sys

A_PATHS = ("tests/saves", "tests/accounts", "tests/api_contract")
C_PATHS = ("tests/rules",)
# What `tests` runs: the playthrough-marked tests have their own jobs.
SELECT = ("-m", "not playthrough")


def shard_args(shard: str) -> list[str]:
    if shard == "a":
        return list(A_PATHS)
    if shard == "b":
        return [f"--ignore={path}" for path in A_PATHS + C_PATHS]
    if shard == "c":
        return list(C_PATHS)
    raise SystemExit(f"unknown shard {shard!r}: a, b or c")


def collected(extra: list[str], select: tuple[str, ...] = SELECT, env: dict[str, str] | None = None) -> set[str]:
    """The node ids pytest collects for these arguments, from its own -q listing (one `path::name` per line)."""
    run = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", *select, *extra],
                         capture_output=True, text=True, check=False, env=env)
    ids = {line for line in run.stdout.splitlines() if "::" in line}
    if run.returncode != 0 or not ids:
        sys.exit(f"collection failed (exit {run.returncode}, {len(ids)} ids):\n{run.stdout[-2000:]}{run.stderr[-2000:]}")
    return ids


def check() -> int:
    whole = collected([])
    a, b, c = (collected(shard_args(name)) for name in "abc")
    print(f"unsharded {len(whole)} tests; shard a {len(a)}, shard b {len(b)}, shard c {len(c)}")
    both, missing, extra = (a & b) | (a & c) | (b & c), whole - a - b - c, (a | b | c) - whole
    for label, ids in (("in both shards", both), ("in neither shard", missing), ("only in a shard", extra)):
        for node in sorted(ids)[:10]:
            print(f"{label}: {node}")
    return 1 if both or missing or extra else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        sys.exit(check())
    if len(sys.argv) < 2:
        sys.exit("usage: python -m tools.shards a|b|c|--check [pytest args]")
    os.execvp(sys.executable, [sys.executable, "-m", "pytest", *SELECT, *shard_args(sys.argv[1]), *sys.argv[2:]])
