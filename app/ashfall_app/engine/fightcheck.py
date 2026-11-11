"""What makes a FightDef valid (DESIGN.txt, "FIGHTS", "CHOICES"). A leaf of rules_check: the rules arrive as an argument
and are never imported."""
from typing import TYPE_CHECKING

from .cards import HELD_PREFIX, CardDef, FightDef, Held, HeldSpeed, Outcome, WhileRunning
from .cardsides import card_costs, card_makes
from .errors import InvalidRulesError
from .fightlines import ODDS_PREFIX, fight_costs, fight_makes
from .ids import StoreId
from .modifiers import Modifier
from .nodes import NODE_PREFIX

if TYPE_CHECKING:
    from .rules import Rules, StandingDef


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidRulesError(message)


def fight_stores(f: FightDef) -> list[StoreId]:
    return [a.store for a in (*fight_costs(f), *fight_makes(f))]


def check_fight(rules: "Rules", where: str, f: FightDef, others: list[StoreId], card: CardDef | None) -> None:
    """A fight of a card (`card`) or a standing action (None). `others`: the stores the runner's own lines list."""
    _require(f.side in {s.id for s in rules.sides}, f"{where}: fight names an unknown side")
    _require(f.threat in {t.id for t in rules.threats}, f"{where}: fight names an unknown threat")
    stores = {s.id for s in rules.stores}
    _require(all(a.quantity > 0 for a in (*f.loses, *f.wounds)), f"{where}: a fight amount must be > 0")
    listed = [*others, *fight_stores(f)]
    _require(all(s in stores for s in listed), f"{where}: a fight line names an unknown store")
    _require(len(set(listed)) == len(listed), f"{where}: a store is listed twice across the runner's lines and its fight")
    if card is not None:
        _require(card.cap is None, f"{where}: a fight card has no cap")
        _require(f.per_hour == 0 and f.fought is None, f"{where}: per_hour and fought belong to a standing fight")
    else:
        _require(f.per_hour > 0, f"{where}: a standing fight needs per_hour > 0")


def _outcomes(rules: "Rules") -> list[Outcome]:
    return [*(o for c in rules.cards for o in (c.outcome, c.finished)), *(t.outcome for t in rules.triggers),
            *(a.outcome for o in rules.offers for a in o.answers)]


def _lines_of(rules: "Rules") -> dict[str, list[StoreId]]:
    """Every runner's stores across all its lines, its fight's included."""
    out = {str(c.id): [*card_makes(c), *card_costs(c)] for c in rules.cards}
    for a in rules.standing:
        out[str(a.id)] = standing_stores(a)
    return out


def standing_stores(a: "StandingDef") -> list[StoreId]:
    return [*(f.store for f in a.makes + a.costs), *(fight_stores(a.fight) if a.fight else ())]


def check_tallies(rules: "Rules") -> None:
    """A tally (lost, fought) is made only by its own fight's line: no other runner's line and no outcome.
    Listed once among its own runner's lines (check_fight), it is never also that runner's cost or input."""
    lines = _lines_of(rules)
    outcome_stores = {a.store for o in _outcomes(rules) for a in o.stores}
    for runner, fight in [(str(c.id), c.fight) for c in rules.cards if c.fight] + [
            (str(a.id), a.fight) for a in rules.standing if a.fight]:
        for tally in (t for t in (fight.lost, fight.fought) if t is not None):
            _require(tally not in outcome_stores, f"{runner}: tally store {tally} is made by an outcome")
            _require(all(tally not in s for r, s in lines.items() if r != runner),
                     f"{runner}: tally store {tally} is on another runner's line")


def check_no_odds_source(modifiers: tuple[Modifier, ...], where: str) -> None:
    _require(not any(str(m.source).startswith(ODDS_PREFIX) for m in modifiers), f"{where}: the odds source is the engine's")
    _require(not any(str(m.source).startswith(HELD_PREFIX) for m in modifiers), f"{where}: the held source is the engine's")
    _require(not any(str(m.source).startswith(NODE_PREFIX) for m in modifiers), f"{where}: the node source is a pick's")


def check_while_running(rules: "Rules", where: str, entries: tuple[Held, ...]) -> None:
    """A card's or a standing action's held entries (DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS", "HELD SPEED"):
    declared sides and declared lanes (never HANDS, which is never declared), each once, amounts >= 1."""
    sides = [w.side for w in entries if isinstance(w, WhileRunning)]
    lanes = [w.lane for w in entries if isinstance(w, HeldSpeed)]
    declared = {d.id for d in rules.sides}
    for s in sides:
        _require(s in declared, f"{where}: while_running names an unknown side {s}")
    for ln in lanes:
        _require(ln in {d.id for d in rules.lanes}, f"{where}: while_running names a lane {ln} that is not declared")
    for w in entries:
        name = f"side {w.side}" if isinstance(w, WhileRunning) else f"lane {w.lane}"
        _require(w.amount_bp >= 1, f"{where}: while_running amount for {name} must be >= 1")
    for s in sides:
        _require(sides.count(s) == 1, f"{where}: while_running names side {s} twice")
    for ln in lanes:
        _require(lanes.count(ln) == 1, f"{where}: while_running names lane {ln} twice")
