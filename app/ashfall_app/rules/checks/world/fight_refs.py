"""The loader's checks on fights: each FightEntry names a side, a threat and stores that exist, and every amount it
takes or adds divides exactly, and its pools' keys are in text; each chain names a standing fight on a group. Content checks on what fights may do (the clock, the cure, the tallies) are
elsewhere. Raises ValueError naming the entry."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from ....engine import QUANTITY_SCALE
from ...refs import fail, ids_by_kind, need

if TYPE_CHECKING:
    from ...entries.entries import FightEntry
    from ...schema import Opening


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
        for store in (f.lost, *(s for s in (f.fought, f.chained) if s is not None)):
            need(where, "store", store, ids["store"])
        for a in (*f.loses, *f.wounds):
            need(where, "store", a.store, ids["store"])
            if (a.items * QUANTITY_SCALE) % a.every != 0:
                fail(where, f"{a.items} per {a.every} {a.store} does not divide exactly into quantity units")
        for key in (*f.won_line_keys, *f.lost_line_keys, *(f.loss_pool or ()), *(f.loss_notes or ()),
                    *([] if f.on_loss_key is None else [f.on_loss_key])):
            if key not in o.text:
                fail(where, f"key {key!r} is not in text")
    check_chains(o)


def check_chains(o: "Opening") -> None:
    """A card's chain names a standing fight on a group threat with a chained tally, and its link lines are in text
    (engine design/spells.txt, "SPELLS")."""
    standing = {a.id: a.fight for a in o.standing}
    members = {t.id: t.members for t in o.threats}
    for c in o.cards:
        if c.chain is None:
            continue
        where, runner = f"card {c.id}", c.chain.runner
        fight = standing.get(runner)
        if fight is None:
            fail(where, f"chain names {runner}, which is not a standing fight")
        elif members.get(fight.threat, 1) < 2:
            fail(where, f"chain names {runner}, whose threat {fight.threat} is not a group")
        elif fight.fought is None or fight.chained is None:
            fail(where, f"chain names {runner}, which has no fought or chained tally")
        for key in c.chain.link_line_keys:
            if key not in o.text:
                fail(where, f"key {key!r} is not in text")
