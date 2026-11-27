"""What makes a chain valid (engine/design/, "SPELLS", "Validation"). A leaf of rules_check: the rules arrive as an
argument and are never imported."""
from typing import TYPE_CHECKING

from ..cards.cards import CardDef, FightDef
from ..loop.cardsides import card_costs, card_makes
from ..core.errors import InvalidRulesError
from .fightcheck import standing_stores
from ..core.ids import StoreId, ThreatId

if TYPE_CHECKING:
    from ..core.rules import Rules


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidRulesError(message)


def check_chains(rules: "Rules") -> None:
    """Threats' members, each card's chain, and every chained tally."""
    for t in rules.threats:
        _require(t.members >= 1, f"threat {t.id}: members must be >= 1")
    groups = {t.id for t in rules.threats if t.members >= 2}
    for c in rules.cards:
        _require(c.fight is None or c.fight.chained is None,
                 f"card {c.id}: chained belongs to a standing fight on a group threat")
        _check_chain(rules, c, groups)
    for a in rules.standing:
        _require(a.fight is None or a.fight.chained is None or a.fight.threat in groups,
                 f"action {a.id}: chained belongs to a standing fight on a group threat")
    _check_chained_tallies(rules)


def _check_chain(rules: "Rules", c: CardDef, groups: set[ThreatId]) -> None:
    chain = c.chain
    if chain is None:
        return
    where = f"card {c.id}"
    _require(c.fight is None, f"{where}: a fight card has no chain")
    runner = next((a for a in rules.standing if a.id == chain.runner), None)
    _require(runner is not None and runner.fight is not None,
             f"{where}: chain names {chain.runner}, which is not a standing fight")
    assert runner is not None and runner.fight is not None
    f: FightDef = runner.fight
    _require(f.threat in groups, f"{where}: chain names {chain.runner}, whose threat {f.threat} is not a group")
    _require(f.fought is not None and f.chained is not None,
             f"{where}: chain names {chain.runner}, which has no fought or chained tally")
    _require(chain.reach >= 1, f"{where}: chain reach must be >= 1")
    _require(len(chain.lines) >= 1, f"{where}: a chain needs at least one line")


def _check_chained_tallies(rules: "Rules") -> None:
    """A chained tally is made only by its chains: no runner's line (its own included), no outcome, and no other
    fight's tally of any kind."""
    lines: list[StoreId] = [*(s for c in rules.cards for s in (*card_makes(c), *card_costs(c))),
                            *(s for a in rules.standing for s in standing_stores(a))]
    outcomes = [*(o for c in rules.cards for o in (c.outcome, c.finished)), *(t.outcome for t in rules.triggers),
                *(a.outcome for o in rules.offers for a in o.answers)]
    made = {a.store for o in outcomes for a in o.stores}
    fights = [f for f in (*(c.fight for c in rules.cards), *(a.fight for a in rules.standing)) if f is not None]
    tallies = [s for f in fights for s in (f.lost, f.fought, f.chained) if s is not None]
    stores = {s.id for s in rules.stores}
    for a in rules.standing:
        tally = a.fight.chained if a.fight is not None else None
        if tally is None:
            continue
        _require(tally in stores, f"action {a.id}: chained tally store {tally} is not declared")
        _require(tally not in lines, f"action {a.id}: chained tally store {tally} is on a runner's line")
        _require(tally not in made, f"action {a.id}: chained tally store {tally} is made by an outcome")
        _require(tallies.count(tally) == 1, f"action {a.id}: chained tally store {tally} is another tally too")
