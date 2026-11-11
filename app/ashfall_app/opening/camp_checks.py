"""The camp's checks: its store and levels, what lifts a held level, and alternatives among the cards lifting one
(engine DESIGN.txt, "THE CAMP")."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .convert import camp_cap, camp_chain
from .refs import fail, need, outcomes

if TYPE_CHECKING:
    from .entries import ModifierEntry
    from .schema import Opening


def check_camp(o: "Opening") -> None:
    if o.camp is None:
        return
    store = next((s for s in o.stores if s.id == o.camp.store), None)
    if store is None:
        fail("camp", f"unknown store {o.camp.store}")
    at = [lv.at_items for lv in o.camp.levels]
    if not at or any(a >= b for a, b in zip(at, at[1:])):
        fail("camp", "needs levels, their at_items strictly increasing")
    if store.cap_items != camp_cap(o.camp):
        fail("camp", f"the store's cap_items must be what its levels allow ({camp_cap(o.camp)})")
    caps = {c.id: c.cap for c in o.cards}
    for n, lv in enumerate(o.camp.levels, start=1):
        if lv.lifted_by and not lv.held:
            fail(f"camp level {n}", "lifted_by names what lifts a held level; this one is not held")
        for card in lv.lifted_by:
            need(f"camp level {n}", "card", card, list(caps))
            if caps[card] is None:
                fail(f"camp level {n}", f"card {card} has no cap, so it never finishes to lift the level")
        if lv.held and not lv.lifted_by and (n != len(o.camp.levels) or lv.line_keys or lv.modifiers):
            fail(f"camp level {n}", "only the last level may be held without lifted_by, and it lands nothing")
        _check_alternatives(o, f"camp level {n}", lv.lifted_by)
    for n, _, bp in camp_chain(o.camp):
        if bp < 1:
            fail(f"camp level {n}", "its step raises the camp cap by less than a basis point: too close to the level "
                 "below for the cap to hold under it or reach it")
    for where, m in [*_camp_modifiers(o), *((w, m) for w, out in outcomes(o) for m in out.modifiers)]:
        if m.target == "cap" and m.id == o.camp.store:
            fail(where, "aims at the camp store's cap, which only the loader's lifts and steps raise")


def _camp_modifiers(o: "Opening") -> "Iterator[tuple[str, ModifierEntry]]":
    assert o.camp is not None
    return ((f"camp level {n}", m) for n, lv in enumerate(o.camp.levels, start=1) for m in lv.modifiers)


def _check_alternatives(o: "Opening", where: str, cards: list[str]) -> None:
    """Two or more cards lifting one level are alternatives: each unlocked only by answers of one offer, and no answer
    unlocking two, so at most one ever finishes (engine DESIGN.txt, "THE CAMP")."""
    if len(cards) < 2:
        return
    others = [*o.start, *(u for c in o.cards for u in (*c.outcome.unlocks, *c.finished.unlocks)),
              *(u for t in o.triggers for u in t.outcome.unlocks)]
    by_card = {card: [(x.id, a.id) for x in o.offers for a in x.answers
                      if any(u.unlock_kind == "card" and u.id == card for u in a.outcome.unlocks)] for card in cards}
    if any(u.unlock_kind == "card" and u.id in by_card for u in others) or any(not v for v in by_card.values()) or \
            len({offer for v in by_card.values() for offer, _ in v}) != 1:
        fail(where, "cards that lift one level must be unlocked only by answers of one offer")
    answers = [a for v in by_card.values() for _, a in v]
    if len(answers) != len(set(answers)):
        fail(where, "an answer unlocks two of the cards that lift one level, so both could finish")

