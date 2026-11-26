"""What a pull request's CI plays of the whole game (docs/engineering.md, "Scope and test budget"), from what changed.

Run from app/: python -m tools.pr_plan --base-tree DIR [--saves DIR] [--full]   prints the plan as JSON; CI's `slice` job
reads it. DIR is a checkout of the commit the pull request is based on; --saves is the restored nightly's saved ends, and
without it every saved end counts as present. Each chapter's own inputs (tests/weektwo/keys.py) are hashed
in that tree and in this one: a chapter whose own inputs differ is touched.

  mode `full`   the label or a dispatch asked for everything: the nightly's chain, each chapter from the saved end before it
  mode `smoke`  a change every chapter reads (the engine, the loader, shared data, a rules' id, beats.yaml), week one's, or one
                the base cannot be compared with: no chapter's saved end before it is the base's, so the day-eight plays of
                the push routes from the start (tests marked `smoke`) stand for the engine. Where the change is one every
                chapter reads or week one's, the `makers` shard plays too, from the start: its readouts read the whole
                game through day twelve and no other job of the pull request reads them
  mode `slice`  only chapters' own files changed: each touched chapter's tests, from the base's saved end of the one before;
                the smoke instead where the last nightly holds no saved end of the chapter before one it would play (`why`)
  mode `none`   no chapter's inputs changed: nothing of week two plays
`chapters` are the touched chapters, `files` the week-two test files changed, `base_keys` the keys the base's saves are under.
`shards` are the week-two shards the slice plays, one job each (a touched chapter's, or all of them when a test file changed),
and `left` the ones in tools/weektwo_shards.py NIGHTLY_ONLY, which the nightly plays; `smoke` has "smoke", and `makers` where the change is one every chapter reads or week one's.
"""
import json
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tests.weektwo import keys
from tools.weektwo_shards import SMOKE, WHOLE_GAME, chapters_of, slice_shards

TESTS = "app/tests/weektwo/"


@dataclass(frozen=True)
class Snap:
    shared: str
    own: dict[str, str]
    key: dict[str, str]


def here() -> Snap:
    return Snap(keys.shared(), {c: keys.own(c) for c in keys.ORDER}, {c: keys.key(c) for c in keys.ORDER})


def snapshot(tree: Path) -> Snap | None:
    """The shared digest, each chapter's own digest and key, as `tree` computes them; None where it has no chapter keys."""
    run = subprocess.run([sys.executable, "-m", "tests.weektwo.keys"], cwd=tree / "app", capture_output=True, text=True,
                         check=False, env={**os.environ, "PYTHONPATH": "."})
    if run.returncode != 0:
        print(f"the base has no chapter keys: {run.stderr.strip().splitlines()[-1:]}", file=sys.stderr)
        return None
    found = json.loads(run.stdout)
    return Snap(str(found["shared"]), {str(c): str(d) for c, d in found["own"].items()},
                {str(c): str(k) for c, k in found["key"].items()})


def changed_files(base_tree: Path) -> list[str]:
    """The files this checkout changes from the commit `base_tree` is at."""
    base = subprocess.run(["git", "-C", str(base_tree), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    run = subprocess.run(["git", "diff", "--name-only", base.stdout.strip(), "HEAD"], capture_output=True, text=True, check=True)
    return run.stdout.split()


Saved = Callable[[str], bool]
"""Whether the base's saved end under this key is held."""


def plan(base: Snap | None, full: bool, changed: list[str], saved: Saved = lambda key: True) -> dict[str, object]:
    now = here()
    files = sorted(f for f in changed if f.startswith(TESTS) and (Path(f).name.startswith("test_") or Path(f).name == "conftest.py"))
    out: dict[str, object] = {"mode": "none", "chapters": [], "files": files, "base_keys": {},
                             "shards": [], "left": []}
    if full:
        return out | {"mode": "full"}
    if base is None:
        return out | {"mode": "smoke", "shards": ["smoke"], "why": "the base has no chapter keys"}
    out["base_keys"] = base.key
    if base.shared != now.shared:
        return out | {"mode": "smoke", "shards": [SMOKE, *sorted(WHOLE_GAME)], "why": "what every chapter reads changed"}
    touched = [c for c in keys.ORDER if base.own.get(c) != now.own[c]]
    if "week1" in touched:
        return out | {"mode": "smoke", "shards": [SMOKE, *sorted(WHOLE_GAME)], "why": "week one changed"}
    if touched or files:
        played, left = slice_shards(touched, bool(files))
        absent = sorted({c for n in played for c in chapters_of(n) if c in keys.ORDER and (b := keys.before(c)) and not saved(base.key[b])})
        if absent:
            return out | {"mode": "smoke", "shards": ["smoke"], "left": [],
                          "why": f"the last nightly holds no saved end of the chapter before {', '.join(absent)}"}
        return out | {"mode": "slice", "chapters": touched, "shards": played, "left": left}
    return out


def main(argv: list[str]) -> int:
    rest = argv[2:]
    found: Saved = lambda key: True
    if rest[:1] == ["--saves"] and len(rest) >= 2:
        root = Path(rest[1])
        found = lambda key: (root / key / "manifest.json").exists()
        rest = rest[2:]
    if argv[:1] != ["--base-tree"] or len(argv) < 2 or rest not in ([], ["--full"]):
        print(__doc__, file=sys.stderr)
        return 2
    tree = Path(argv[1])
    print(json.dumps(plan(snapshot(tree), rest == ["--full"], changed_files(tree), found)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
