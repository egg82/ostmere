"""CI's `chapter-saves` job (docs/engineering.md, "Fast from the start"): the saved ends for today's key, from the runner
cache or written.

    python -m tools.saves_cache CACHE_DIR [PART...]   # from app/; ASHFALL_SAVES_ROOT is where the saves are put

CACHE_DIR holds one `<key>.tar` per key (the job's `cache:` path). A tar for today's key is unpacked into the saves root
(a hit); without one the writer runs and its output is tarred into CACHE_DIR (a miss). Only the newest KEEP tars are kept.
With PARTs, only those are written (tools/chapter_saves.py, `--write`): CI caches each part under its own key.
"""
import subprocess
import sys
import tarfile
import time
from collections.abc import Callable
from pathlib import Path

KEEP = 3


def unpack(tar: Path, root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar) as t:
        t.extractall(root, filter="data")


def pack(saves: Path, tar: Path) -> None:
    tar.parent.mkdir(parents=True, exist_ok=True)
    partial = tar.with_suffix(".partial")
    with tarfile.open(partial, "w") as t:
        t.add(saves, arcname=saves.name)
    partial.replace(tar)


def prune(cache: Path, keep: int = KEEP) -> list[str]:
    """Delete all but the `keep` newest tars (and any partial one); the names removed."""
    for stray in cache.glob("*.partial"):
        stray.unlink()
    tars = sorted(cache.glob("*.tar"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in tars[keep:]:
        old.unlink()
    return [p.name for p in tars[keep:]]


def run(cache: Path, root: Path, key: str, write: Callable[[], None]) -> tuple[str, int]:
    """("hit" or "miss", the tar's bytes): the saves for `key` under `root`, unpacked from `cache` or written by `write`."""
    tar = cache / f"{key}.tar"
    if tar.exists():
        unpack(tar, root)
        tar.touch()
        result = "hit"
    else:
        write()
        pack(root / key, tar)
        result = "miss"
    prune(cache)
    return result, tar.stat().st_size


def writer(parts: list[str]) -> Callable[[], None]:
    def write() -> None:
        subprocess.run([sys.executable, "tools/chapter_saves.py", "--write", *parts], check=True)
    return write


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    from tests.weektwo import ends
    started = time.monotonic()
    result, size = run(Path(argv[0]), ends.root(), ends.key(), writer(argv[1:]))
    print(f"event=chapter_saves.cache key={ends.key()[:8]} parts={','.join(argv[1:]) or 'all'} result={result} "
          f"seconds={time.monotonic() - started:.0f} bytes={size}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
