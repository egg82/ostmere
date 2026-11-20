"""View.store_rows: each ledger store's net as set and where it heads (CONTRACT.txt, "Store rows"). The rates are
setrates.py's, the same running set as goal_rows, so a dry run's goals and stores are one simulation."""
from .. import engine as e
from ..engine.mixruns import mix_entries
from ..engine.rates import Running
from ..engine.sides import costs, makes
from . import setrates as sr
from . import store_models as s
from .goalrows import lands


def store_rows(save: e.Save, rules: e.Rules, v: e.View) -> list[s.StoreRow]:
    now = sr.as_set(save, rules)
    mixed = {st for card, _, _ in mix_entries(save, rules) for st in makes(rules, card) | costs(rules, card)}
    return [_row(save, rules, now, ln, ln.store in mixed) for ln in v.ledger]


def _row(save: e.Save, rules: e.Rules, now: Running, ln: e.LedgerLine, mixed: bool) -> s.StoreRow:
    net = sr.net_per_hour(save, rules, now, ln.store)
    held = e.segment(save, rules, ln.store).start_value
    if net < 0:
        heading, at = s.Heading.EMPTIES, save.time if held <= 0 else lands(save.time, held, -net)
    elif net > 0 and held < ln.cap:
        heading, at = s.Heading.FILLS, lands(save.time, ln.cap - held, net)
    else:
        heading, at = s.Heading.STEADY, None
    return s.StoreRow(store=str(ln.store), per_hour=net, heading=heading, at=at, mixed=mixed)
