"""The engine's speed gate: this tree against its merge-base, timed on the same machine in the same job.

Run from app/: python -m tools.bench_ab BASE_APP_DIR [rounds] [repeats]. BASE_APP_DIR is the merge-base's app/
directory. Each round runs tools.engine_bench in a process on the base tree and one on this tree (the order flips every
round, so neither side always runs first), `repeats` samples per workload per process; each attempt prints both sides' fastest samples. A workload fails when this
tree's fastest sample is more than SLOWER_MAX over the base's fastest, in two attempts (see main). CPU speed, runner load and CPU type cancel;
only the diff between the trees is left. engine_bench.py itself is copied into the base tree so both sides time the
same workload with the same clock, whatever the base had. Exit 1 is a slowdown, 2 a run that could not measure.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD_APP = HERE.parent
SLOWER_MAX = 0.12  # over A/A noise (docs/engineering.md, "The engine's speed gate"), under a 15% slowdown
WORKLOADS = ("reading", "steps")


def run_once(app: Path, repeats: int) -> dict[str, list[float]]:
    """One process on `app`'s tree: each workload's samples."""
    env = {"PYTHONPATH": str(app), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    out = subprocess.run([sys.executable, "-m", "tools.engine_bench", str(repeats), "--json"], cwd=app,
                         env={**os.environ, **env}, capture_output=True, text=True, check=False)
    if out.returncode != 0:
        sys.stderr.write(out.stderr[-3000:])
        raise SystemExit(2)
    found = json.loads(out.stdout.strip().splitlines()[-1])
    return {w: found[w]["samples"] for w in WORKLOADS}


def verdict(base: dict[str, list[float]], head: dict[str, list[float]], limit: float = SLOWER_MAX) -> dict[str, float]:
    """Each workload's head min over base min; raises when a side has no samples (nothing measured is not a pass)."""
    ratios: dict[str, float] = {}
    for w in WORKLOADS:
        if not base.get(w) or not head.get(w):
            raise ValueError(f"no samples for {w}")
        ratios[w] = min(head[w]) / min(base[w])
    return ratios


def fastest(base: dict[str, list[float]], head: dict[str, list[float]]) -> str:
    """Each side's fastest sample per workload in CPU seconds, the absolute numbers the ratio hides."""
    return " ".join(f"{w}: base={min(base[w]):.3f}s head={min(head[w]):.3f}s" for w in WORKLOADS)


def attempt(base_app: Path, rounds: int, repeats: int) -> dict[str, float]:
    """`rounds` rounds of one process per side, the order flipping each round; each workload's head/base."""
    base: dict[str, list[float]] = {w: [] for w in WORKLOADS}
    head: dict[str, list[float]] = {w: [] for w in WORKLOADS}
    for r in range(rounds):
        order = [("base", base_app), ("head", HEAD_APP)][::1 if r % 2 == 0 else -1]
        for name, app in order:
            for w, samples in run_once(app, repeats).items():
                (base if name == "base" else head)[w].extend(samples)
    print("fastest " + fastest(base, head))
    return verdict(base, head)


def main(base_app: Path, rounds: int, repeats: int) -> int:
    """A workload over the limit is measured again on fresh rounds and fails only if it is over both times: a busy
    neighbour can make one attempt's fastest samples lopsided, and does not do it twice."""
    shutil.copyfile(HERE / "engine_bench.py", base_app / "tools" / "engine_bench.py")
    first = attempt(base_app, rounds, repeats)
    print("attempt 1: " + " ".join(f"{w}={r:.3f}" for w, r in first.items()) + f" max={1 + SLOWER_MAX:.2f}")
    over = [w for w, r in first.items() if r > 1 + SLOWER_MAX]
    if not over:
        return 0
    second = attempt(base_app, rounds, repeats)
    print("attempt 2: " + " ".join(f"{w}={r:.3f}" for w, r in second.items()))
    slower = [w for w in over if second[w] > 1 + SLOWER_MAX]
    for w in slower:
        print(f"SLOWER: {w} is over {1 + SLOWER_MAX:.2f}x the merge-base in both attempts")
    return int(bool(slower))


if __name__ == "__main__":
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(Path(pos[0]).resolve(), int(pos[1]) if len(pos) > 1 else 4, int(pos[2]) if len(pos) > 2 else 3))
