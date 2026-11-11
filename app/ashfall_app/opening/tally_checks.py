"""The checks on tally stores (StoreEntry.tally): a count only outcomes add to, which gates read. The arrivals count
is one: the first arrival's trigger adds 1, and each join adds 1 (docs/design/day-three-plan.md, item 4). Raises
ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def check_tallies(o: "Opening") -> None:
    """No card or standing action spends a tally store (a cost, an input or a drain), and, once content declares one,
    every outcome that joins people adds one to a tally store per join, a join marked `counted` excepted."""
    tallies = {s.id for s in o.stores if s.tally}
    if not tallies:
        return
    for c in o.cards:
        if {f.store for f in c.costs} & tallies or {a.store for a in (*c.inputs, *c.drains)} & tallies:
            fail(f"card {c.id}", "takes a tally store, which only an outcome adds to and a gate reads")
    for a in o.standing:
        if {f.store for f in a.costs} & tallies:
            fail(f"action {a.id}", "takes a tally store, which only an outcome adds to and a gate reads")
    for where, out in outcomes(o):
        added = sum(a.items for a in out.stores if a.store in tallies)
        arriving = sum(not j.counted for j in out.joins)
        if out.joins and added != arriving:
            fail(where, f"joins {arriving} not yet counted but adds {added} to a tally store: each such join adds one")
