"""The built Rules as the finite-supply check reads them (finite_checks.py): every card and standing action as what it
takes and gives per unit of its work, how many units it can run, and whether progress can count on it being in play.
Ids and fields only. Base amounts, before any modifier."""
from collections.abc import Iterator
from dataclasses import dataclass
from fractions import Fraction

from ..engine import CardDef, Outcome, Rules, StandingDef, StoreId, Unlock, UnlockKind
from ..engine.fightlines import fight_costs, fight_makes

HOUR = 3600


@dataclass(frozen=True)
class Runner:
    """A card (unit: one completion at a full share) or a standing action (unit: an hour). takes and gives: quantity
    units per unit, lumps and flows together, drains among the takes. stops: the takes that stop it when dry (all but
    drains, which never do). units: how many it can run, None for no limit. sure: it is put in play by something
    progress passes through (the start, a trigger, a sure card), not only by an answer."""

    id: str
    takes: dict[StoreId, Fraction]
    stops: frozenset[StoreId]
    gives: dict[StoreId, Fraction]
    units: int | None
    sure: bool
    card: CardDef | None


def runners(rules: Rules) -> list[Runner]:
    sure = sure_unlocks(rules)
    raised = _raises(rules)
    found = [_card(c, sum(raised.get(str(c.id), ())), Unlock(UnlockKind.CARD, c.id) in sure) for c in rules.cards]
    return found + [_standing(a, Unlock(UnlockKind.ACTION, a.id) in sure) for a in rules.standing]


def sure_outcomes(rules: Rules, sure: frozenset[Unlock]) -> Iterator[tuple[Outcome, int]]:
    """Each outcome progress can count on landing, with how many times it lands at most: every trigger once, and a sure
    card's finished once per reach (a sure capped card's outcome lands per completion, so it is read as its gives).
    Answers are left out: the player may decline them."""
    yield from ((t.outcome, 1) for t in rules.triggers)
    raised = _raises(rules)
    for c in rules.cards:
        if c.cap is not None and Unlock(UnlockKind.CARD, c.id) in sure:
            yield c.finished, 1 + len(raised.get(str(c.id), ()))


def sure_unlocks(rules: Rules) -> frozenset[Unlock]:
    """What the start, the triggers, and the outcomes of cards already sure unlock, to the fixed point."""
    if rules.opening is None:
        return frozenset(Unlock(UnlockKind.CARD, c.id) for c in rules.cards) | frozenset(
            Unlock(UnlockKind.ACTION, a.id) for a in rules.standing)
    sure = set(rules.opening) | {u for t in rules.triggers for u in t.outcome.unlocks}
    grew = True
    while grew:
        grew = False
        for c in rules.cards:
            if Unlock(UnlockKind.CARD, c.id) in sure:
                new = set(c.outcome.unlocks + c.finished.unlocks) - sure
                sure |= new
                grew = grew or bool(new)
    return frozenset(sure)


def _card(c: CardDef, raised: int, sure: bool) -> Runner:
    takes: dict[StoreId, Fraction] = {}
    gives: dict[StoreId, Fraction] = {}
    for f in c.costs:
        _add(takes, f.store, Fraction(f.per_hour * c.work_s))
    for a in (*c.inputs, *c.drains, *(fight_costs(c.fight) if c.fight else ())):
        _add(takes, a.store, Fraction(a.quantity))
    for f in c.makes:
        _add(gives, f.store, Fraction(f.per_hour * c.work_s))
    for a in (*c.outcome.stores, *(fight_makes(c.fight) if c.fight else ())):
        _add(gives, a.store, Fraction(a.quantity))
    stops = frozenset(takes) - {a.store for a in c.drains}
    return Runner(str(c.id), takes, stops, gives, None if c.cap is None else c.cap + raised, sure, c)


def _standing(a: StandingDef, sure: bool) -> Runner:
    takes: dict[StoreId, Fraction] = {}
    gives: dict[StoreId, Fraction] = {}
    for f in a.costs:
        _add(takes, f.store, Fraction(f.per_hour * HOUR))
    for f in a.makes:
        _add(gives, f.store, Fraction(f.per_hour * HOUR))
    return Runner(str(a.id), takes, frozenset(takes), gives, None, sure, None)


def _add(into: dict[StoreId, Fraction], store: StoreId, q: Fraction) -> None:
    into[store] = into.get(store, Fraction(0)) + q


def _raises(rules: Rules) -> dict[str, list[int]]:
    """Every raise each capped card's cap can get, one entry per landing: a raise in a trigger, an answer or a finished
    lands once, one in a capped card's outcome once per completion."""
    found: dict[str, list[int]] = {}
    outcomes = [(t.outcome, 1) for t in rules.triggers] + [(a.outcome, 1) for x in rules.offers for a in x.answers]
    outcomes += [(c.finished, 1) for c in rules.cards] + [(c.outcome, c.cap or 0) for c in rules.cards]
    for out, times in outcomes:
        for r in out.raises:
            found.setdefault(str(r.card), []).extend([r.by] * times)
    return found
