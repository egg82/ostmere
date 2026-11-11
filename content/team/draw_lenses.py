#!/usr/bin/env python3
"""Draw one lens per writer from lenses.txt, distinct within a task, reproducible from the task id.

Usage: draw_lenses.py <task id> [--writers 3]
Prints one "writer-N<TAB>lens" line per writer. The same task id always draws the same lenses, so a rerun or a
reviewer can check the draw; a new task id draws afresh. Stdlib only.
"""
import argparse
import hashlib
import os
import random


def draw(task, writers, lenses):
    if writers > len(lenses):
        raise SystemExit("only %d lenses for %d writers" % (len(lenses), writers))
    seed = int.from_bytes(hashlib.sha256(task.encode()).digest()[:8], "big")
    return random.Random(seed).sample(lenses, writers)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--writers", type=int, default=3)
    a = ap.parse_args()
    lenses = [ln.strip() for ln in open(os.path.join(here, "lenses.txt")) if ln.strip()]
    for i, lens in enumerate(draw(a.task, a.writers, lenses), 1):
        print("writer-%d\t%s" % (i, lens))


if __name__ == "__main__":
    main()
