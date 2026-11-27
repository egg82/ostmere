"""memo.KeyedMemo: a build kept per key while the parts are the very same objects, found by a dict probe."""
from ashfall_app.engine.core.memo import KeyedMemo


def test_a_key_under_the_same_parts_builds_once_and_other_parts_or_keys_build_again():
    memo: KeyedMemo[list[int]] = KeyedMemo()
    a, b = ("a",), ("b",)
    built: list[int] = []

    def build(n: int):
        def run() -> list[int]:
            built.append(n)
            return [n]
        return run

    first = memo.get((a, b), ("k", 1), build(1))
    assert memo.get((a, b), ("k", 1), build(2)) is first, "same parts, equal key: kept"
    assert memo.get((a, b), ("k", 1.0), build(3)) is first, "an equal key is the same key"
    assert memo.get((a, b), ("k", 2), build(4)) == [4], "another key builds"
    assert memo.get((tuple(["a"]), b), ("k", 1), build(5)) == [5], "an equal but different part builds"
    assert built == [1, 4, 5]


def test_a_full_group_starts_again_and_the_oldest_group_goes():
    memo: KeyedMemo[int] = KeyedMemo(groups=2, size=2)
    parts = [(i,) for i in range(3)]
    for p in parts:
        memo.get((p,), 0, lambda: 1)
    built: list[str] = []
    memo.get((parts[2],), 0, lambda: built.append("new") or 1)
    memo.get((parts[0],), 0, lambda: built.append("oldest") or 1)
    assert built == ["oldest"]
    memo.get((parts[2],), 1, lambda: 1)
    memo.get((parts[2],), 2, lambda: built.append("full") or 1)
    memo.get((parts[2],), 1, lambda: built.append("restarted") or 1)
    assert built == ["oldest", "full", "restarted"]
