"""The loader's checks on fights: each FightEntry names a side, a threat and stores that exist, and every amount it
takes or adds divides exactly, and its pools' keys are in text. Content checks on what fights may do (the clock, the cure, the tallies) are
elsewhere. Raises ValueError naming the entry."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..engine import QUANTITY_SCALE
from .refs import fail, ids_by_kind, need

if TYPE_CHECKING:
    from .entries import FightEntry
    from .schema import Opening


def fights(o: "Opening") -> "Iterator[tuple[str, FightEntry]]":
    """Every fight with where it sits: cards first, then standing actions (the engine's view order)."""
    for c in o.cards:
        if c.fight is not None:
            yield f"card {c.id}", c.fight
    for a in o.standing:
        if a.fight is not None:
            yield f"action {a.id}", a.fight


def check_fights(o: "Opening") -> None:
    ids = ids_by_kind(o)
    for where, f in fights(o):
        need(where, "side", f.side, ids["side"])
        need(where, "threat", f.threat, ids["threat"])
        for store in (f.lost, *([] if f.fought is None else [f.fought])):
            need(where, "store", store, ids["store"])
        for a in (*f.loses, *f.wounds):
            need(where, "store", a.store, ids["store"])
            if (a.items * QUANTITY_SCALE) % a.every != 0:
                fail(where, f"{a.items} per {a.every} {a.store} does not divide exactly into quantity units")
        for key in (*f.won_line_keys, *f.lost_line_keys):
            if key not in o.text:
                fail(where, f"key {key!r} is not in text")
