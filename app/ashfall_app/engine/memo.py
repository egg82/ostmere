"""Derived state read many times from one save within an instant, kept by identity (docs/engineering.md, "Dirty Flag
and caches for expensive derived state"). Saves and rules are immutable values, so whatever is built from a save and
its rules stays true for that very pair; a SaveMemo keeps the last pairs it was asked about (one, or `size`) and
their values, and builds again for any other (rules None: what is built reads the save alone). Its entries are swapped
whole: a reader sees the old ones or the new, never half of each, so a concurrent caller can only cost a rebuild. Never shared state: the value
is the build's own, the same with or without the memo."""
from collections.abc import Callable

from .rules import Rules
from .state import Save


class SaveMemo[T]:
    def __init__(self, size: int = 1) -> None:
        self._entries: tuple[tuple[Save, Rules | None, T], ...] = ()
        self._size = size

    def get(self, save: Save, rules: Rules | None, build: Callable[[], T]) -> T:
        entries = self._entries
        for entry in entries:
            if entry[0] is save and entry[1] is rules:
                return entry[2]
        value = build()
        self._entries = ((save, rules, value), *entries[:self._size - 1])
        return value

    def holds(self, save: Save, rules: Rules | None) -> bool:
        """Whether get would return a kept value for this pair, without building one."""
        return any(entry[0] is save and entry[1] is rules for entry in self._entries)

    def put(self, save: Save, rules: Rules | None, value: T) -> None:
        """Keep `value` for this pair, which must be what get would build for it."""
        self._entries = ((save, rules, value), *self._entries[:self._size - 1])


class PartsMemo[T]:
    """A SaveMemo for what is built from a few of a save's fields alone, kept across saves: an entry holds while each
    part is the very object it was built from (fields a save carries over unchanged stay the same object), and `same`,
    for an input that is rebuilt each time, is equal to what it was. It keeps the last `size` entries, newest first, so
    an advance whose state cycles (a rule and a chip flipping on and off, instant after instant) finds the state it
    left; the tuple of entries is swapped whole, as SaveMemo's entry is."""

    def __init__(self, size: int = 1) -> None:
        self._entries: tuple[tuple[tuple[object, ...], object, T], ...] = ()
        self._size = size

    def get(self, parts: tuple[object, ...], build: Callable[[], T], same: object = None) -> T:
        entries = self._entries
        for entry in entries:
            kept = entry[0]
            if len(kept) != len(parts):
                continue
            for a, b in zip(kept, parts):
                if a is not b:
                    break
            else:
                if entry[1] == same:
                    return entry[2]
        value = build()
        self._entries = ((parts, same, value), *entries[:self._size - 1])
        return value
