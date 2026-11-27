"""The content's fight and find infos, from the rules' fights and the opening's entries (contract/fights.txt, "FIGHTS")."""
from ... import engine as e
from ...rules.entries.entries import CardEntry, FightEntry
from ...rules.schema import Opening
from ..world import content_models as cm
from .chain_models import ChainInfo


def fight_info(f: e.FightDef | None, entry: FightEntry | None) -> cm.FightInfo | None:
    if f is None:
        return None
    return cm.FightInfo(side=f.side, threat=f.threat, loses=[cm.Amount(store=a.store, quantity=a.quantity) for a in f.loses],
                        wounds=[cm.Amount(store=a.store, quantity=a.quantity) for a in f.wounds],
                        won_line_keys=[] if entry is None else list(entry.won_line_keys),
                        lost_line_keys=[] if entry is None else list(entry.lost_line_keys),
                        loss_pool=None if entry is None else entry.loss_pool,
                        loss_notes=None if entry is None else entry.loss_notes,
                        on_loss_key=None if entry is None else entry.on_loss_key)


def find_infos(o: Opening) -> list[cm.FindInfo]:
    return [cm.FindInfo(line_key=t.outcome.found_line_key, store=t.outcome.stores[0].store,
                        quantity=e.units(t.outcome.stores[0].items))
            for t in o.triggers if t.outcome.found_line_key is not None]


def chain_info(c: CardEntry) -> ChainInfo | None:
    """A working's chain as the page reads it (contract/spells.txt, "SPELLS")."""
    if c.chain is None:
        return None
    return ChainInfo(runner=c.chain.runner, link_line_keys=list(c.chain.link_line_keys))
