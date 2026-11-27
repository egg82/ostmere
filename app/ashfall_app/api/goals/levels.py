"""View.levels: the segment of each store the page reads as a level though it has no ledger line (contract/fights.txt, "FIGHTS",
"read a level"): each store a lost fight adds to (FightDef.wounds) in content order, then each store the scene manifest
reads that the ledger does not list. The segment is the raw sampled amount."""
from ... import engine as e
from .. import convert
from . import fight_models as fm


def levels(save: e.Save, rules: e.Rules, v: e.View, scene: frozenset[str] = frozenset()) -> list[fm.StoreLevel]:
    fights = [x.fight for x in (*rules.cards, *rules.standing) if x.fight is not None]
    stores = dict.fromkeys(a.store for f in fights for a in f.wounds)
    listed = {ln.store for ln in v.ledger}
    known = {s.id for s in rules.stores}
    stores.update(dict.fromkeys(e.StoreId(s) for s in sorted(scene) if s in known and e.StoreId(s) not in listed))
    return [fm.StoreLevel(store=str(s), segment=convert.segment(e.segment(save, rules, s))) for s in stores]
