"""CI's saved-ends cache (tools/saves_cache.py): a miss writes and keeps a tar, a hit unpacks it without writing, and only
the newest few are kept."""
import os
from collections.abc import Callable
from pathlib import Path

from tools import saves_cache


def writes(root: Path, key: str, calls: list[str]) -> Callable[[], None]:
    def write() -> None:
        calls.append(key)
        (root / key).mkdir(parents=True)
        (root / key / "manifest.json").write_text(key)
    return write


def test_a_miss_writes_and_a_later_hit_unpacks_without_writing(tmp_path: Path):
    cache = tmp_path / "cache"
    calls: list[str] = []
    first = tmp_path / "first"
    result, size = saves_cache.run(cache, first, "k1", writes(first, "k1", calls))
    assert (result, calls) == ("miss", ["k1"]) and size > 0
    second = tmp_path / "second"
    result, size2 = saves_cache.run(cache, second, "k1", writes(second, "k1", calls))
    assert (result, calls, size2) == ("hit", ["k1"], size)
    assert (second / "k1" / "manifest.json").read_text() == "k1"


def test_only_the_newest_tars_are_kept(tmp_path: Path):
    cache = tmp_path / "cache"
    calls: list[str] = []
    for i in range(saves_cache.KEEP + 2):
        root = tmp_path / f"root{i}"
        saves_cache.run(cache, root, f"k{i}", writes(root, f"k{i}", calls))
        os.utime(cache / f"k{i}.tar", (i, i))
    kept = sorted(p.name for p in cache.glob("*.tar"))
    assert len(kept) == saves_cache.KEEP
    assert "k0.tar" not in kept and f"k{saves_cache.KEEP + 1}.tar" in kept
