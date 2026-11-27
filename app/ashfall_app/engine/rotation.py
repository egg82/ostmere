"""A pool of lines said in turn: the k-th draw of a seeded shuffle bag (design/core.txt, "Chips"). The same draw as the
page's (client/src/game/ledger/fights.ts, bagged), so a pool reads alike wherever it is worded."""
from collections.abc import Callable, Sequence

_MASK = 0xFFFFFFFF


def _seeded(key: str) -> Callable[[], float]:
    """A 32-bit FNV-1a hash of the key seeds a mulberry32 generator (fights.ts, seeded)."""
    h = 0x811C9DC5
    for ch in key:
        h = ((h ^ ord(ch)) * 0x01000193) & _MASK
    a = h

    def draw() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & _MASK
        t = ((a ^ (a >> 15)) * (1 | a)) & _MASK
        t = ((t + ((t ^ (t >> 7)) * (61 | t))) & _MASK) ^ t
        return ((t ^ (t >> 14)) & _MASK) / 4294967296
    return draw


def _shuffled[T](xs: Sequence[T], draw: Callable[[], float]) -> list[T]:
    """A Fisher-Yates shuffle of a copy, by `draw`."""
    bag = list(xs)
    for i in range(len(bag) - 1, 0, -1):
        j = int(draw() * (i + 1))
        bag[i], bag[j] = bag[j], bag[i]
    return bag


def _round(key: str, pool: Sequence[str], r: int) -> list[str]:
    """Round r of the bag: the pool shuffled by a draw keyed by `key` and r, its first swapped with its second when it
    would repeat the last of round r - 1 (with three or more lines the swap never moves a round's last)."""
    bag = _shuffled(pool, _seeded(f"{key}|{r}"))
    if r > 0 and bag[0] == _shuffled(pool, _seeded(f"{key}|{r - 1}"))[-1]:
        bag[0], bag[1] = bag[1], bag[0]
    return bag


def bagged(key: str, pool: Sequence[str], k: int) -> str:
    """The k-th draw (from 0) of `pool`'s shuffle bag keyed by `key`: each line once a round, never one twice in a row
    (a pool of two keeps its first round's order)."""
    if len(pool) <= 2:
        return _shuffled(pool, _seeded(f"{key}|0"))[k % len(pool)]
    return _round(key, pool, k // len(pool))[k % len(pool)]
