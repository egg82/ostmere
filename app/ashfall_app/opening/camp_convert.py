"""The camp's cap steps and the card lifts they make, from the authored levels (engine design/camp.txt, "THE CAMP"). Pure."""
from dataclasses import replace
from typing import TYPE_CHECKING

from ..engine import BP, CardDef, Modifier, ModifierKind, SourceId, StoreCap, StoreId, ceil_div, units

if TYPE_CHECKING:
    from .camp_entries import CampEntry, CampLevelEntry


def camp_lands(lv: "CampLevelEntry") -> bool:
    """A level the loader makes a trigger for: every level but a held one nothing lifts."""
    return not lv.held or bool(lv.lifted_by)


def camp_cap(camp: "CampEntry") -> int:
    """The camp store's cap in items: one under the first held level a step lifts (the bar holds just below its
    marker), else the last level's at_items."""
    lifted = [lv.at_items for lv in camp.levels if lv.held and lv.lifted_by]
    return lifted[0] - 1 if lifted else camp.levels[-1].at_items


def camp_chain(camp: "CampEntry") -> list[tuple[int, str | None, int]]:
    """The camp cap's steps in order (engine design/camp.txt, "THE CAMP"): (level n, the lifting card or None for the step
    to_camp_n, the raise in bp). Each step's target is exact, the least add that reaches a level or the greatest that
    stays under a held one, and its raise is that target less the previous step's, so the raises telescope."""
    first = next((i for i, lv in enumerate(camp.levels) if lv.held and lv.lifted_by), None)
    if first is None:
        return []
    base = units(camp_cap(camp))
    steps: list[tuple[int, str | None, int]] = []
    prev = 0
    for n, lv in enumerate(camp.levels[first:], start=first + 1):
        reach = ceil_div(units(lv.at_items) * BP, base) - BP
        if n > first + 1:
            target = reach - 1 if lv.held else reach
            steps.append((n, None, target - prev))
            prev = target
        if lv.held and lv.lifted_by:
            steps += [(n, card, reach - prev) for card in lv.lifted_by]
            prev = reach
    return steps


def camp_raise(camp: "CampEntry", bp: int, source: str) -> Modifier:
    return Modifier(StoreCap(StoreId(camp.store)), ModifierKind.ADD_BP, bp, SourceId(source))


def camp_lifts(camp: "CampEntry") -> list[tuple[str, Modifier]]:
    """(card, raise) for each card of each held level's lifted_by: the raise its finish lands (camp_chain)."""
    return [(card, camp_raise(camp, bp, card)) for _, card, bp in camp_chain(camp) if card is not None]


def lifts_by_card(camp: "CampEntry | None") -> dict[str, list[Modifier]]:
    """camp_lifts grouped by card, read once per build."""
    found: dict[str, list[Modifier]] = {}
    for card, m in camp_lifts(camp) if camp is not None else ():
        found.setdefault(card, []).append(m)
    return found


def with_lifts(card: CardDef, lifts: dict[str, list[Modifier]]) -> CardDef:
    mods = tuple(lifts.get(card.id, ()))
    if not mods:
        return card
    return replace(card, finished=replace(card.finished, modifiers=card.finished.modifiers + mods))
