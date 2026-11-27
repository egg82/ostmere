"""What a card's face can draw before a tap, and the check that it draws every require that can refuse the tap
(docs/decisions/principles.md, "Progress is stated, never hinted": a gate on progress may not hide). A require is drawn
when it is:
- `at_least` on a store the player is shown (shown_stores): its have/need row;
- `at_least` on a skill's level or another card's completions: its level or step row;
- `at_least` on a clock with a part of the day (StoreEntry.clock): when it opens ("opens after dark");
- `at_least` on another clock (a store the player is never shown that only standing actions make) as the card's only
  precondition, the clock's maker unlocked before the card can be: the card's countdown.
A reach stake's store (CardInfo.reach) is a require too: the track laid is a line that joins the ledger only once full,
so the face draws it against the next reach, and must have a store it may draw.
A ruled lane's cards are its tasks, run by the player's rules and never tapped, so they are not checked. The same
stores are the ones a cause may name (api/world/line_causes.py). Raises ValueError naming the store (refs.fail); ids only,
since the owner reads CI."""
from collections.abc import Iterable
from functools import reduce
from typing import TYPE_CHECKING

from ...refs import fail, outcomes
from .stake_checks import reach_stops

if TYPE_CHECKING:
    from ...entries.entries import CardEntry, ConditionEntry, OutcomeEntry
    from ...schema import Opening

Key = tuple[str, str]
"""An unlock: (unlock_kind, id)."""
Site = tuple[frozenset[Key], tuple["ConditionEntry", ...]]
"""One place an unlock is granted: the unlocks held there by construction, and the conditions that hold there."""


def shown_stores(o: "Opening") -> frozenset[str]:
    """The stores whose amount the page draws: unlocked by the start or some outcome and not hidden, or a tally (a count
    the game keeps, drawn as a figure though it has no ledger line)."""
    unlocked = {u.id for u in o.start if u.unlock_kind == "store"}
    unlocked |= {u.id for _, out in outcomes(o) for u in out.unlocks if u.unlock_kind == "store"}
    return frozenset(s.id for s in o.stores if (s.id in unlocked and not s.hidden) or s.tally)


def timed_stores(o: "Opening") -> frozenset[str]:
    """The clocks a condition on reads as a time of day (StoreEntry.clock)."""
    return frozenset(s.id for s in o.stores if s.clock is not None)


def check_clocks(o: "Opening") -> None:
    """A store with a part of the day is a clock: never shown, made only by standing actions."""
    shown, clocks = shown_stores(o), standing_clocks(o)
    for s in o.stores:
        if s.clock is not None and (s.id in shown or s.id not in clocks):
            fail(f"store {s.id}", f"reads as a time of day ({s.clock}) but is "
                 + ("shown to the player" if s.id in shown else "not made by standing actions alone"))


def undrawn(o: "Opening") -> list[tuple[str, str, str]]:
    """(card, subject kind, id) for each require of a tappable card that its face cannot draw; a reach stake's store's
    kind is "reach"."""
    ruled = {x.id for x in o.lanes if x.ruled}
    drawn = shown_stores(o) | timed_stores(o)
    clocks, before = standing_clocks(o), unlocked_before(o)
    tappable = [c for c in o.cards if c.lane not in ruled]
    return [*((c.id, r.subject_kind or r.test, r.id or "") for c in tappable for r in c.requires
              if not _drawn(c, r, drawn, clocks, before.get(("card", c.id), frozenset()))),
            *((c.id, "reach", s) for c in tappable if c.stake == "reach"
              for s in dict.fromkeys(s for s, _ in reach_stops(o, c)) if s not in drawn)]


def _drawn(c: "CardEntry", r: "ConditionEntry", drawn: frozenset[str], clocks: dict[str, frozenset[str]],
           before: frozenset[Key]) -> bool:
    if r.test != "at_least":
        return False
    if r.subject_kind in ("skill_level", "card_count"):
        return True
    if r.subject_kind != "store" or r.id is None:
        return False
    if r.id in drawn:
        return True
    alone = len(c.requires) == 1 and not c.inputs
    return alone and any(("action", a) in before for a in clocks.get(r.id, ()))


def standing_clocks(o: "Opening") -> dict[str, frozenset[str]]:
    """Each store only standing actions make (no card, outcome or start amount adds to it), with its makers."""
    granted = {s.store for _, out in outcomes(o) for s in out.stores}
    granted |= {f.store for c in o.cards for f in c.makes}
    makers: dict[str, set[str]] = {}
    for a in o.standing:
        for f in a.makes:
            makers.setdefault(f.store, set()).add(a.id)
    starting = {s.id for s in o.stores if s.initial_items > 0}
    return {s: frozenset(m) for s, m in makers.items() if s not in granted and s not in starting}


def unlocked_before(o: "Opening") -> dict[Key, frozenset[Key]]:
    """Each unlock some outcome grants, with the unlocks every way of granting it holds first: the greatest fixed point
    over its sites (a card's outcome holds that card and its requires; a trigger's, its conditions; an answer's, its
    offer). The start's unlocks hold nothing first."""
    sites = _sites(o)
    start = {(u.unlock_kind, u.id) for u in o.start}
    clocks = standing_clocks(o)
    every = frozenset(sites) | start
    before: dict[Key, frozenset[Key]] = {k: (frozenset() if k in start else every) for k in every}
    changed = True
    while changed:
        changed = False
        for k, ways in sites.items():
            if k in start:
                continue
            held = _common([_held(own, conds, before, clocks) for own, conds in ways])
            if held != before[k]:
                before[k], changed = held, True
    return before


def _sites(o: "Opening") -> dict[Key, list[Site]]:
    found: dict[Key, list[Site]] = {}

    def add(out: "OutcomeEntry", own: frozenset[Key], conds: Iterable["ConditionEntry"]) -> None:
        for u in out.unlocks:
            found.setdefault((u.unlock_kind, u.id), []).append((own, tuple(conds)))

    for c in o.cards:
        for out in (c.outcome, c.finished):
            add(out, frozenset({("card", c.id)}), c.requires)
    for t in o.triggers:
        add(t.outcome, frozenset(), (t.when, *t.requires))
    for x in o.offers:
        for a in x.answers:
            add(a.outcome, frozenset({("offer", x.id)}), (x.gate, *x.requires))
    return found


def _held(own: frozenset[Key], conds: tuple["ConditionEntry", ...], before: dict[Key, frozenset[Key]],
          clocks: dict[str, frozenset[str]]) -> frozenset[Key]:
    held = set(own)
    for k in own:
        held |= before.get(k, frozenset())
    for c in conds:
        held |= _held_by(c, before, clocks)
    return frozenset(held)


def _held_by(c: "ConditionEntry", before: dict[Key, frozenset[Key]], clocks: dict[str, frozenset[str]]
             ) -> frozenset[Key]:
    """What a met condition shows is unlocked: what it reads, and what that holds first. A store reached that only
    standing actions make holds what every one of its makers holds."""
    if c.test != "at_least" or c.value < 1 or c.id is None:
        return frozenset()
    key: Key | None = None
    if c.subject_kind == "unlocked" and c.unlock_kind is not None:
        key = (c.unlock_kind, c.id)
    elif c.subject_kind == "card_count":
        key = ("card", c.id)
    elif c.subject_kind == "skill_level" and c.value >= 2:
        key = ("skill", c.id)
    elif c.subject_kind == "store" and c.id in clocks:
        return _common([frozenset({("action", a)}) | before.get(("action", a), frozenset()) for a in clocks[c.id]])
    return frozenset() if key is None else frozenset({key}) | before.get(key, frozenset())


def _common(sets: list[frozenset[Key]]) -> frozenset[Key]:
    return reduce(lambda a, b: a & b, sets)
