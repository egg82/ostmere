"""View.levels: each store a lost fight adds to (FightDef.wounds), as its segment, in content order; the store has no
ledger line, so the page reads its level here (CONTRACT.txt, "FIGHTS", "read a level")."""
from .. import engine as e
from . import convert
from . import fight_models as fm


def levels(save: e.Save, rules: e.Rules) -> list[fm.StoreLevel]:
    fights = [x.fight for x in (*rules.cards, *rules.standing) if x.fight is not None]
    stores = dict.fromkeys(a.store for f in fights for a in f.wounds)
    return [fm.StoreLevel(store=str(s), segment=convert.segment(e.segment(save, rules, s))) for s in stores]
