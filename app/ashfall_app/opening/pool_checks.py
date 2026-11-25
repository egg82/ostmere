"""Every line a source says again and again is drawn from a pool of at least MIN_POOL different keys (a chip's off
lines, a fight's won and lost lines, a people band's), so no one line comes up often enough to read as stuck. Counts
keys, never reads their words. Raises ValueError naming the source."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .fight_refs import fights
from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening

MIN_POOL = 6
"""The fewest different keys a repeating source's pool may hold."""


def pools(o: "Opening") -> Iterator[tuple[str, list[str]]]:
    """Each pool a repeating source draws from, with where it sits: a chip's off lines, a fight's won lines and lost
    lines, each people band's lines. An empty pool is none: the chip says nothing as it clears, the fight takes the
    page's stock ui.fight line (UI words naming the runner, not the journal's)."""
    for ch in o.chips:
        if ch.off_line_keys:
            yield f"chip {ch.id} off_line_keys", ch.off_line_keys
    for where, f in fights(o):
        if f.won_line_keys:
            yield f"{where} won_line_keys", f.won_line_keys
        if lost := f.loss_pool or f.lost_line_keys:
            yield f"{where} {'lost_line_keys' if f.loss_pool is None else 'loss_pool'}", lost
    if o.people is not None:
        for way, bands in (("came", o.people.came), ("went", o.people.went)):
            yield from ((f"people {way} at_least {b.at_least}", b.keys) for b in bands)


def check_pools(o: "Opening") -> None:
    """Fails on a pool of fewer than MIN_POOL different keys, and on an uncapped card's line: the engine says that one
    key every tap (CardDef.lines), so it can be no pool."""
    for where, keys in pools(o):
        if len(set(keys)) < MIN_POOL:
            fail(where, f"{len(set(keys))} different lines; a line said again and again draws from at least {MIN_POOL}")
    for c in o.cards:
        if c.cap is None and c.line_keys:
            fail(f"card {c.id}", "an uncapped card's line_keys would say one line every tap; give it none")
