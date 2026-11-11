"""The lines a FightDef adds to its runner, as per-fight amounts (DESIGN.txt, "FIGHTS"): what a lost fight takes and
what it, and every fight, adds. A leaf: it imports only card data, so rule validation and the line tables can use it."""
from .cards import Amount, FightDef
from .units import QUANTITY_SCALE

ODDS_PREFIX = "odds:"
"""Every odds entry's source starts with it, followed by its runner's id; content may not use such a source."""


def fight_makes(f: FightDef) -> tuple[Amount, ...]:
    """The make lines a fight adds: wounds, then one unit of the lost tally and, if it has one, of the fought tally."""
    tallies = (f.lost,) if f.fought is None else (f.lost, f.fought)
    return f.wounds + tuple(Amount(s, QUANTITY_SCALE) for s in tallies)


def fight_costs(f: FightDef) -> tuple[Amount, ...]:
    return f.loses
