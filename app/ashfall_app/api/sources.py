"""Where each input a card in play needs comes from (View Card.needs' gate and makers; CONTRACT.txt, "Cards"), read off
the content's makers (opening/makers.py), the save's fired triggers and the engine's view."""
from collections.abc import Mapping
from dataclasses import dataclass

from .. import engine as e
from ..opening.makers import card_makers, granted_by, standing_makers
from ..opening.schema import Opening


@dataclass(frozen=True)
class StoreSources:
    """A store's makers (card ids in card order, then standing action ids) and the triggers that grant it (ids, content
    order)."""

    makers: tuple[str, ...]
    grants: tuple[str, ...]


@dataclass(frozen=True)
class Source:
    """One need's: the condition of the trigger that grants its store, while unmet and the need short (None once met,
    or when something makes the store), the makers in play: cards in view.cards, standing actions in view.standing, and
    whether it is spent: short, its store one nothing in play can make again (engine spent_stores) and every trigger
    granting it fired."""

    gate: e.Condition | None
    makers: tuple[str, ...]
    spent: bool


Sources = Mapping[tuple[str, str], Source]
"""Keyed by (card, store)."""


def store_sources(o: Opening) -> dict[str, StoreSources]:
    """Every store's makers and grants, from the content."""
    return {s.id: StoreSources((*card_makers(o, s.id), *standing_makers(o, s.id)), tuple(granted_by(o, s.id)))
            for s in o.stores}


def sources(save: e.Save, rules: e.Rules, v: e.View, table: Mapping[str, StoreSources]) -> dict[tuple[str, str], Source]:
    """A Source for each need of each card in view.cards."""
    in_play = {str(c.card) for c in v.cards} | {str(a.action) for a in v.standing}
    pos = {str(t.id): i for i, t in enumerate(rules.triggers)}
    gone = e.spent_stores(save, rules)
    out: dict[tuple[str, str], Source] = {}
    for c in v.cards:
        for n in c.needs:
            s = table.get(str(n.store), StoreSources((), ()))
            short = e.value_at(n.segment, v.time) < n.quantity
            gate = None if s.makers or not short else _gate(save, rules, pos, s.grants)
            spent = short and n.store in gone and all(_fired(save, pos, t) for t in s.grants)
            out[(str(c.card), str(n.store))] = Source(gate, tuple(m for m in s.makers if m in in_play), spent)
    return out


def _fired(save: e.Save, pos: Mapping[str, int], trigger: str) -> bool:
    i = pos.get(trigger)
    return i is not None and i < len(save.fired) and save.fired[i]


def _gate(save: e.Save, rules: e.Rules, pos: Mapping[str, int], grants: tuple[str, ...]) -> e.Condition | None:
    """The first grant not fired yet whose condition a need row can show: a skill's level or a card's completions."""
    for t in grants:
        i = pos.get(t)
        if i is None or _fired(save, pos, t):
            continue
        when = rules.triggers[i].when
        if isinstance(when, e.AtLeast) and isinstance(when.subject, (e.SkillLevel, e.CardCount)):
            return when
    return None
