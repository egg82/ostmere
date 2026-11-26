"""CI's `chapter-saves` jobs (docs/engineering.md, "Fast from the start"): the saved ends of a part's chapters for today's
keys, from the runner cache or written.

    python -m tools.saves_cache CACHE_DIR PART...   # from app/; ASHFALL_SAVES_ROOT is where the saves are put

CACHE_DIR holds one `<key>.tar` per parts' key (tools/chapter_saves.py, `parts_key`: the job's `cache:` path). A tar for
today's key holds the directories of the chapters the parts write and is unpacked into the saves root (a hit); without one
the writer runs and those directories are tarred into CACHE_DIR (a miss). Only the newest KEEP tars are kept.
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


def pack(root: Path, dirs: list[str], tar: Path) -> None:
    tar.parent.mkdir(parents=True, exist_ok=True)
    partial = tar.with_suffix(".partial")
    with tarfile.open(partial, "w") as t:
        for name in dirs:
            t.add(root / name, arcname=name)
    partial.replace(tar)


def prune(cache: Path, keep: int = KEEP) -> list[str]:
    """Delete all but the `keep` newest tars (and any partial one); the names removed."""
    for stray in cache.glob("*.partial"):
        stray.unlink()
    tars = sorted(cache.glob("*.tar"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in tars[keep:]:
        old.unlink()
    return [p.name for p in tars[keep:]]


def run(cache: Path, root: Path, key: str, dirs: list[str], write: Callable[[], None]) -> tuple[str, int]:
    """("hit" or "miss", the tar's bytes): the `dirs` for `key` under `root`, unpacked from `cache` or written by `write`."""
    tar = cache / f"{key}.tar"
    if tar.exists():
        unpack(tar, root)
        tar.touch()
        result = "hit"
    else:
        write()
        pack(root, dirs, tar)
        result = "miss"
    prune(cache)
    return result, tar.stat().st_size


def writer(parts: list[str]) -> Callable[[], None]:
    def write() -> None:
        subprocess.run([sys.executable, "tools/chapter_saves.py", "--write", *parts], check=True)
    return write


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    from tests.weektwo import ends
    from tools.chapter_saves import chapters_of, parts_key
    started, parts = time.monotonic(), frozenset(argv[1:])
    key = parts_key(parts)
    result, size = run(Path(argv[0]), ends.root(), key, [ends.key(c) for c in chapters_of(parts)], writer(argv[1:]))
    print(f"event=chapter_saves.cache key={key[:8]} parts={','.join(argv[1:])} result={result} "
          f"seconds={time.monotonic() - started:.0f} bytes={size}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
